"""批量并发获取多篇笔记详情。

CDPClient 已改为线程安全（单 reader 线程 + event 分发），
ThreadPoolExecutor(max_workers=3) 并发开 3 个 tab 同时 fetch，
总耗时从 O(n) 降低到 O(n/3)。
"""

from __future__ import annotations

import contextlib
import logging
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from .cdp import Browser
from .feed_detail import get_feed_detail
from .types import Feed, FeedDetailResponse

logger = logging.getLogger(__name__)

MAX_WORKERS = 3


def _log_progress(msg: str) -> None:
    """输出结构化进度到 stderr，供 LLM 和用户实时查看。"""
    print(msg, file=sys.stderr, flush=True)


def batch_get_details(
    browser: Browser,
    feeds: list[Feed],
    fast_mode: bool = False,
) -> list[FeedDetailResponse | None]:
    """并发批量获取笔记详情（最多 3 个 tab 同时运行）。

    Args:
        browser: 已连接的 Browser 实例（CDPClient 线程安全）。
        feeds: 需要获取详情的 Feed 列表。
        fast_mode: 是否启用快速模式（减少 headless 等待延迟）。

    Returns:
        与 feeds 同序的详情列表，失败的条目为 None。
    """
    if not feeds:
        return []

    total = len(feeds)
    results: list[FeedDetailResponse | None] = [None] * total
    completed_count = 0
    counter_lock = threading.Lock()

    def fetch_one(idx: int, feed: Feed) -> tuple[int, FeedDetailResponse | None]:
        nonlocal completed_count
        title = feed.note_card.display_title or feed.id
        page = browser.new_page()
        try:
            detail = get_feed_detail(page, feed.id, feed.xsec_token, fast_mode=fast_mode)
            with counter_lock:
                completed_count += 1
                _log_progress(f'[fetch] {completed_count}/{total} 完成 ✓ "{title}"')
            return idx, detail
        except Exception as e:
            logger.warning("获取详情失败 (feed=%s): %s", feed.id, e)
            with counter_lock:
                completed_count += 1
                _log_progress(f'[fetch] {completed_count}/{total} 失败 ✗ "{title}" ({e})')
            return idx, None
        finally:
            with contextlib.suppress(Exception):
                browser.close_page(page)

    _log_progress(f"[fetch] 并发获取 {total} 条详情 (workers={MAX_WORKERS})...")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(fetch_one, i, feed): i for i, feed in enumerate(feeds)}
        for future in as_completed(futures):
            idx, detail = future.result()
            results[idx] = detail

    return results
