---
name: xhs-interact
description: |
  小红书社交互动技能。发表评论、回复评论、点赞、收藏。
  当用户要求评论、回复、点赞或收藏小红书帖子时触发。
version: 0.0.1.dev
---

# xhs-interact

## 命令列表

所有命令支持全局参数 `--account <名称>`（写在子命令之前）来指定账号。
所有命令均需要 `--feed-id` 和 `--xsec-token`（从 xhs-explore 输出中获取）。

| 命令 | 主要参数 | 返回 |
|------|----------|------|
| `post-comment` | `--feed-id`，`--xsec-token`，`--content` | `{success}` |
| `reply-comment` | `--feed-id`，`--xsec-token`，`--content`，`[--comment-id\|--user-id]` | `{success}` |
| `like-feed` | `--feed-id`，`--xsec-token`，`[--unlike]` | `{success}` |
| `favorite-feed` | `--feed-id`，`--xsec-token`，`[--unfavorite]` | `{success}` |

点赞和收藏操作是幂等的，重复执行不会出错。

## 必须向用户确认

发送评论或回复前，必须向用户确认内容，获得明确同意后再执行。

## 退出码

`0` 成功 · `1` 未登录 · `2` 错误
