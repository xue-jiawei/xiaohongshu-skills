"""批量获取多篇笔记详情（消除 LLM 逐条编排开销）。

由于 CDP WebSocket 不支持并发，详情获取仍为串行，但通过将多篇笔记的获取
合并到一次 CLI 调用中，消除了 LLM 逐条解析 JSON → 提取 ID → 再次调用的
编排开销（每轮 2-5 秒），使总耗时从 O(n * (fetch + LLM)) 降低到 O(n * fetch)。
"""

from __future__ import annotations

import contextlib
import logging
import sys

from .cdp import Browser
from .feed_detail import get_feed_detail
from .types import Feed, FeedDetailResponse

logger = logging.getLogger(__name__)


def _log_progress(msg: str) -> None:
    """输出结构化进度到 stderr，供 LLM 和用户实时查看。"""
    print(msg, file=sys.stderr, flush=True)


def batch_get_details(
    browser: Browser,
    feeds: list[Feed],
    fast_mode: bool = False,
) -> list[FeedDetailResponse | None]:
    """批量获取多篇笔记详情。

    为每篇笔记开一个新 tab，获取详情后关闭，串行执行。
    主要优势：消除 LLM 逐条编排的上下文切换开销。

    Args:
        browser: 已连接的 Browser 实例。
        feeds: 需要获取详情的 Feed 列表。

    Returns:
        与 feeds 同序的详情列表，失败的条目为 None。
    """
    if not feeds:
        return []

    results: list[FeedDetailResponse | None] = [None] * len(feeds)
    total = len(feeds)

    for i, feed in enumerate(feeds):
        title = feed.note_card.display_title or feed.id
        _log_progress(f'[fetch] {i + 1}/{total} 正在加载: "{title}"')

        page = browser.new_page()
        try:
            detail = get_feed_detail(page, feed.id, feed.xsec_token, fast_mode=fast_mode)
            results[i] = detail
            _log_progress(f"[fetch] {i + 1}/{total} 完成 ✓")
        except Exception as e:
            logger.warning("获取详情失败 (feed=%s): %s", feed.id, e)
            _log_progress(f"[fetch] {i + 1}/{total} 失败 ✗ ({e})")
        finally:
            with contextlib.suppress(Exception):
                browser.close_page(page)

    return results
