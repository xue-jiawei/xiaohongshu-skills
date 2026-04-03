---
name: xhs-content-ops
description: |
  小红书复合内容运营技能。组合搜索、详情、发布、互动等能力完成运营工作流。
  当用户要求竞品分析、热点追踪、内容创作、互动管理等复合任务时触发。
version: 0.0.1.dev
---

# xhs-content-ops

编排多个 CLI 命令完成多步骤运营任务。每步完成后向用户汇报进度。

所有命令支持全局参数 `--account <名称>`（写在子命令之前）来指定账号。

## 本技能使用的命令

| 命令 | 主要参数 | 返回 |
|------|----------|------|
| `search-feeds` | `--keyword`，`[--sort-by]`，`[--publish-time]`，`[--note-type]` | `{feeds: [{id, xsec_token, title, ...}]}` |
| `get-feed-detail` | `--feed-id`，`--xsec-token` | `{note: {title, desc, ...}, comments: [...]}` |
| `post-comment` | `--feed-id`，`--xsec-token`，`--content` | `{success}` |
| `like-feed` | `--feed-id`，`--xsec-token` | `{success}` |
| `favorite-feed` | `--feed-id`，`--xsec-token` | `{success}` |

发布步骤遵循 xhs-publish 的约束（用户确认、取消时 save-draft）。
评论/回复步骤遵循 xhs-interact 的约束（发送前用户确认）。

### --sort-by 可选值

`综合` · `最新` · `最多点赞` · `最多评论` · `最多收藏`

## 工作流程

### 竞品分析

```
search-feeds --keyword <目标> --sort-by 最多点赞
→ 从结果中选取 3–5 篇高互动帖子
→ 逐一 get-feed-detail
→ 输出分析报告：标题风格、内容结构、话题标签、互动数据对比
```

### 热点追踪

```
search-feeds --keyword <话题> --sort-by 最新 --publish-time 一周内
search-feeds --keyword <话题> --sort-by 最多点赞
→ 对高互动帖子 get-feed-detail
→ 输出：热度排名、爆款内容特征、选题建议
```

### 内容创作

```
search-feeds --keyword <主题> --sort-by 最多点赞
→ 对 2–3 篇参考帖子 get-feed-detail
→ 基于分析辅助用户生成草稿（标题/正文/标签，遵循 xhs-publish 标题长度规则）
→ 用户确认后走 xhs-publish 发布流程
```

### 互动管理

```
search-feeds --keyword <目标> --sort-by 最新
→ 对选定帖子 get-feed-detail
→ 生成评论建议 → 用户确认 → post-comment
→ 可选：like-feed / favorite-feed
→ 每次互动之间保持 30–60 秒间隔
```

## 退出码

`0` 成功 · `1` 未登录 · `2` 错误
