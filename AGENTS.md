# xiaohongshu-skills

小红书自动化 Codex / Claude Code Skills，基于 Python CDP 浏览器自动化引擎。

## Git 工作流

- 直接在main branch 开发，commit，push
- 不需要新建branch

## 开发命令

```bash
uv sync                    # 安装依赖
uv run ruff check .        # Lint 检查
uv run ruff format .       # 代码格式化
uv run pytest              # 运行测试
```

## 架构

双层结构：`scripts/` 是 Python CDP 自动化引擎，`skills/` 是 Codex Skills 定义（SKILL.md 格式）。

- `scripts/xhs/` — 核心自动化库（模块化，每个功能一个文件）
- `scripts/cli.py` — 统一 CLI 入口，32 个子命令，JSON 结构化输出
- `scripts/publish_pipeline.py` — 发布编排器（含图片下载和登录检查）
- `skills/*/SKILL.md` — 指导 Codex 如何调用 scripts/

### 调用方式

```bash
python scripts/cli.py check-login
python scripts/cli.py search-feeds --keyword "关键词"
python scripts/cli.py publish --title-file t.txt --content-file c.txt --images pic.jpg
python scripts/publish_pipeline.py --title-file t.txt --content-file c.txt --images URL1
```

## 代码规范

- 行长度上限 100 字符
- 完整 type hints，使用 `from __future__ import annotations`
- 异常继承 `XHSError`（`xhs/errors.py`）
- CLI exit code：0=成功，1=未登录，2=错误
- 用户可见错误信息使用中文
- JSON 输出 `ensure_ascii=False`

### 安全约束

- 发布类操作必须有用户确认机制
- 文件路径必须使用绝对路径
- 敏感内容通过文件传递，不内联到命令行参数
- Chrome Profile 目录隔离账号 cookies

## CLI 子命令对照表

### 认证

| CLI 子命令 | 说明 |
|--|--|
| `check-login` | 检查登录状态（未登录时自动返回二维码） |
| `get-qrcode` | 获取登录二维码截图并立即返回（非阻塞） |
| `wait-login` | 等待扫码登录完成（配合 `get-qrcode` 使用） |
| `login` | 扫码登录（阻塞等待，适合本地终端） |
| `send-code --phone` | 分步手机登录第一步：发送验证码 |
| `verify-code --code` | 分步手机登录第二步：提交验证码 |
| `phone-login` | 手机号+验证码登录（交互式，适合本地终端） |
| `delete-cookies` | 退出登录并清除本地 cookies |
| `start-browser` | 仅启动 Chrome，不执行其他操作 |

### 账号管理

| CLI 子命令 | 说明 |
|--|--|
| `add-account --name` | 添加命名账号，自动分配独立端口（从 9223 起） |
| `list-accounts` | 列出所有命名账号及端口 |
| `remove-account --name` | 删除命名账号 |
| `set-default-account --name` | 设置默认账号 |

### 搜索与浏览

| CLI 子命令 | 说明 |
|--|--|
| `search-and-fetch` | 搜索关键词 + 并发批量获取前 N 条详情（推荐） |
| `list-and-fetch` | 获取首页推荐 + 并发批量获取前 N 条详情（推荐） |
| `search-feeds` | 搜索笔记列表（仅返回摘要，不含详情） |
| `list-feeds` | 获取首页推荐 Feed 列表（仅返回摘要） |
| `get-feed-detail` | 获取单篇笔记详情和评论 |
| `user-profile` | 获取用户主页信息和全部笔记 |

### 互动

| CLI 子命令 | 说明 |
|--|--|
| `post-comment` | 对笔记发表评论 |
| `reply-comment` | 回复指定评论或用户 |
| `like-feed` | 点赞（`--unlike` 取消点赞） |
| `favorite-feed` | 收藏（`--unfavorite` 取消收藏） |

### 发布

| CLI 子命令 | 说明 |
|--|--|
| `publish` | 图文一步发布 |
| `publish-video` | 视频一步发布 |
| `fill-publish` | 填写图文表单（不发布，等待用户确认） |
| `fill-publish-video` | 填写视频表单（不发布，等待用户确认） |
| `click-publish` | 点击发布按钮（配合 `fill-*` 使用） |
| `save-draft` | 保存为草稿（用户取消时调用，防止内容丢失） |
| `long-article` | 长文模式：填写内容并触发一键排版 |
| `select-template` | 选择长文排版模板 |
| `next-step` | 长文发布：进入发布页并填写描述 |
