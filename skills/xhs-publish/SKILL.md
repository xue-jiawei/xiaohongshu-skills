---
name: xhs-publish
description: |
  小红书内容发布技能。支持图文发布、视频发布、长文发布、定时发布、标签、可见性设置。
  当用户要求发布内容到小红书、上传图文、上传视频、发长文时触发。
version: 0.0.1.dev
---

# xhs-publish

## 命令列表

所有命令支持全局参数 `--account <名称>`（写在子命令之前）来指定账号。

| 命令 | 主要参数 | 返回 |
|------|----------|------|
| `fill-publish` | `--title-file`，`--content-file`，`--images` | `{success, status: "表单已填写，等待确认发布"}` |
| `fill-publish-video` | `--title-file`，`--content-file`，`--video` | `{success, status}` |
| `click-publish` | — | `{success, status: "发布完成"}` |
| `save-draft` | — | `{success, status: "内容已保存到草稿箱"}` |
| `publish` | `--title-file`，`--content-file`，`--images` | `{success}` |
| `publish-video` | `--title-file`，`--content-file`，`--video` | `{success}` |
| `long-article` | `--title-file`，`--content-file`，`[--images]` | `{success, templates: [...]}` |
| `select-template` | `--name` | `{success}` |
| `next-step` | `--content-file` | `{success}` |

可选公共参数：`--tags 标签1 标签2`（最多 10 个）· `--schedule-at ISO8601时间` · `--original` · `--visibility "仅自己可见"|"仅互关好友可见"`

## 推荐发布流程：分步确认

`fill-publish` 填写后保持浏览器 tab 打开，用户可在浏览器中预览再决定。

```bash
# 第一步：填写表单（不发布）
uv run python scripts/cli.py fill-publish \
  --title-file /tmp/title.txt \
  --content-file /tmp/content.txt \
  --images "/绝对路径/pic.jpg"

# 第二步：通过 AskUserQuestion 让用户在浏览器中确认预览

# 第三步（确认发布）
uv run python scripts/cli.py click-publish

# 第三步（取消发布）→ 必须保存草稿，否则内容丢失
uv run python scripts/cli.py save-draft
```

`publish`（一步到位）跳过预览确认，仅在用户已明确审核内容后使用。

## 重要行为

**图片：** `--images` 同时支持本地路径和 HTTP/HTTPS URL，脚本自动下载 URL 图片，禁止手动 wget/curl。

**标题长度：** 最多 20 个单位。汉字/全角符号 = 1 单位；每 2 个 ASCII 字符 = 1 单位（单个 ASCII 向上取整为 1）。写入文件前先校验，超长需重写标题。

**标签：** 正文末尾的 `#话题` 会被自动提取并合并到 tags，最多 10 个，超出部分静默丢弃。

**文件路径：** `--title-file`、`--content-file`、`--video`、`--images` 本地路径必须为绝对路径，先写入 `/tmp/` 文件再传参。

**无头模式未登录：** 检查 exit code 1 响应中的 `action` 字段：
- `"switched_to_headed"` → 已切换为有窗口模式，提示用户扫码
- `"login_required"` → 无显示器服务器，通过 xhs-auth 手机登录

## 长文发布流程

长文标题无 20 字限制，使用独立编辑器。

```bash
# 第一步：填写内容并触发一键排版
uv run python scripts/cli.py long-article \
  --title-file /tmp/title.txt \
  --content-file /tmp/content.txt

# 第二步：向用户展示模板列表，让用户选择
uv run python scripts/cli.py select-template --name "模板名"

# 第三步：进入发布页，填写描述（超过 1000 字自动截断至 800 字）
uv run python scripts/cli.py next-step --content-file /tmp/desc.txt

# 第四步：用户确认后发布
uv run python scripts/cli.py click-publish
```

## 从网页 URL 提取图片

用 WebFetch 抓取页面后：
- 优先取 `<img>` 标签的 `data-src`（懒加载真实图片），而非 `src`
- 跳过占位图：路径含 `/shims/`、`/placeholder`、`1x1.png`、`16x9.png` 等
- 只取正文内容区域图片，跳过 logo、图标、视频缩略图
- 图片 URL 必须以 `.jpg`、`.jpeg`、`.png`、`.webp`、`.gif` 结尾

## 必须向用户确认

发布前必须通过 `AskUserQuestion` 展示最终标题、正文、图片/视频，获得用户明确确认后再执行发布命令。

## 退出码

`0` 成功 · `1` 未登录（查看 `action` 字段） · `2` 错误
