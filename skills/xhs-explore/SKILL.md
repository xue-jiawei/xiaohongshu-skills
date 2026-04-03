---
name: xhs-explore
description: |
  小红书知识探索技能。搜索小红书内容作为参考资料和知识来源。
  当用户需要了解某个话题、调研某个领域、寻找灵感或参考时触发。
version: 0.0.1.dev
---

# xhs-explore

## 命令列表

所有命令支持全局参数 `--account <名称>`（写在子命令之前）来指定账号。

| 命令 | 主要参数 | 返回 |
|------|----------|------|
| `search-and-fetch` | `--keyword`（必填），`[--top-n 20]`，筛选参数 | JSON，含 `output_file` 路径 |
| `list-and-fetch` | `[--top-n 20]` | JSON，含 `output_file` 路径 |
| `user-profile` | `--user-id`，`--xsec-token` | JSON（用户信息 + 全部帖子） |

`search-and-fetch` 和 `list-and-fetch` 自动以无头模式运行，无需添加 `--headless`。

### search-and-fetch 筛选参数

| 参数 | 可选值 |
|------|--------|
| `--sort-by` | `综合` · `最新` · `最多点赞` · `最多评论` · `最多收藏` |
| `--note-type` | `不限` · `图文` · `视频` |
| `--publish-time` | `不限` · `一天内` · `一周内` · `半年内` |
| `--search-scope` | `不限` · `已看过` · `未看过` · `已关注` |
| `--location` | `不限` · `同城` · `附近` |

## 输出格式

`search-and-fetch` 和 `list-and-fetch` 返回：

```json
{
  "source": "search",
  "keyword": "关键词",
  "total_feeds": 20,
  "fetched_details": 5,
  "output_file": "/绝对路径/output/abc123def456.md"
}
```

用 Read 工具读取 `output_file`，文件结构如下：

```
# 小红书搜索: "关键词"
> 2026-04-03 | 共 20 条 | 已获取详情 5 条

---

## 1. 标题
`feed_id:67abc123 | xsec_token:XSEC_TOKEN | user_id:USER_ID`
点赞 1.2K | 收藏 800 | 评论 234

正文内容...

**热门评论**
- [120赞] 评论内容...
```

内部会优先选取有互动（点赞数 > 0）的帖子；不足时回退到全部结果。

某条详情获取失败时，文件中会有标注，可用其 `feed_id` + `xsec_token` 单独调用 `get-feed-detail` 重试。

## 深入发布者主页

`user_id` 和 `xsec_token` 在 MD 文件每篇帖子的元数据行中。用于进一步探索：

```bash
uv run python scripts/cli.py user-profile \
  --user-id <MD文件中的user_id> \
  --xsec-token <MD文件中的xsec_token>
```

## 退出码

`0` 成功 · `1` 未登录 · `2` 错误
