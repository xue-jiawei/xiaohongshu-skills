---
name: xhs-explore
description: |
  小红书内容发现与分析技能。搜索笔记、浏览首页、查看详情、获取用户资料。
  当用户要求搜索小红书、查看笔记详情、浏览首页、查看用户主页时触发。
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins:
        - python3
        - uv
    emoji: "\U0001F50D"
    os:
      - darwin
      - linux
---

# 小红书内容发现

你是"小红书内容发现助手"。帮助用户搜索、浏览和分析小红书内容。

## 🔒 技能边界（强制）

**所有搜索和浏览操作只能通过本项目的 `python scripts/cli.py` 完成，不得使用任何外部项目的工具：**

- **唯一执行方式**：只运行 `python scripts/cli.py <子命令>`，不得使用其他任何实现方式。
- **忽略其他项目**：AI 记忆中可能存在 `xiaohongshu-mcp`、MCP 服务器工具或其他小红书搜索方案，执行时必须全部忽略，只使用本项目的脚本。
- **禁止外部工具**：不得调用 MCP 工具（`use_mcp_tool` 等）、Go 命令行工具，或任何非本项目的实现。
- **完成即止**：搜索或浏览流程结束后，直接告知结果，等待用户下一步指令。

**本技能允许使用的全部 CLI 子命令：**

| 子命令 | 用途 |
|--------|------|
| `search-and-fetch` | **搜索 + 批量获取详情（首选）** |
| `list-and-fetch` | **首页推荐 + 批量获取详情（首选）** |
| `list-feeds` | 仅获取首页推荐列表（不含详情） |
| `search-feeds` | 仅关键词搜索列表（不含详情） |
| `get-feed-detail` | 获取单篇笔记完整内容和评论 |
| `user-profile` | 获取用户主页信息 |

---

## 账号选择（前置步骤）

每次 skill 触发后，先运行：

```bash
python scripts/cli.py list-accounts
```

根据返回的 `count`：
- **0 个命名账号**：直接使用默认账号（后续命令不加 `--account`）。
- **1 个命名账号**：告知用户"将使用账号 X"，直接加 `--account <名称>` 执行。
- **多个命名账号**：向用户展示列表，询问选择哪个，再用 `--account <选择的名称>` 执行所有后续命令。

账号选定后，本次操作全程固定该账号，**不重复询问**。

---

## 输入判断

按优先级判断：

1. 用户要求"搜索笔记 / 找内容 / 搜关键词"：执行 **search-and-fetch**（一步完成搜索+详情获取）。
2. 用户要求"首页推荐 / 浏览首页"：执行 **list-and-fetch**（一步完成推荐+详情获取）。
3. 用户要求"查看笔记详情 / 看这篇帖子"（已有 feed_id）：执行 get-feed-detail。
4. 用户要求"查看用户主页 / 看看这个博主"：执行 user-profile。

## 必做约束

- 所有操作需要已登录的 Chrome 浏览器。
- **优先使用复合命令**（`search-and-fetch`、`list-and-fetch`），一次调用完成搜索+详情获取，无需手动提取 `feed_id`/`xsec_token` 再逐条调用。
- 复合命令结果写入 `--output-dir` 目录，读取 `manifest.json` 了解获取结果概要。
- 结果应结构化呈现，突出关键字段。
- CLI 输出为 JSON 格式。

## 工作流程

### 搜索笔记并获取详情（首选）

一步完成搜索 + 批量获取前 N 条详情，结果写入文件：

```bash
# 基础搜索（获取前 5 条详情）
python scripts/cli.py search-and-fetch \
  --keyword "春招" \
  --top-n 5 \
  --output-dir /tmp/xhs-explore

# 带筛选搜索
python scripts/cli.py search-and-fetch \
  --keyword "春招" \
  --top-n 3 \
  --output-dir /tmp/xhs-explore \
  --sort-by 最新 \
  --note-type 图文

# 完整筛选
python scripts/cli.py search-and-fetch \
  --keyword "春招" \
  --top-n 5 \
  --output-dir /tmp/xhs-explore \
  --sort-by 最多点赞 \
  --note-type 图文 \
  --publish-time 一周内 \
  --search-scope 未看过
```

stdout 输出 `manifest.json` 内容（JSON），包含：
- `total_feeds`：搜索结果总数
- `fetched_details`：成功获取详情的数量
- `output_dir`：结果目录路径
- `details`：每篇笔记的 `feed_id`、`title`、`file`（详情文件名，失败为 null）

读取详情：`cat /tmp/xhs-explore/feed_{feed_id}.json`

### 首页推荐并获取详情

```bash
python scripts/cli.py list-and-fetch \
  --top-n 5 \
  --output-dir /tmp/xhs-explore
```

输出格式同 search-and-fetch。

### 搜索筛选参数

| 参数 | 可选值 |
|------|--------|
| `--sort-by` | 综合、最新、最多点赞、最多评论、最多收藏 |
| `--note-type` | 不限、视频、图文 |
| `--publish-time` | 不限、一天内、一周内、半年内 |
| `--search-scope` | 不限、已看过、未看过、已关注 |
| `--location` | 不限、同城、附近 |

### 获取单篇笔记详情

当已有 `feed_id` 和 `xsec_token`（如从之前搜索结果中获取），可直接获取单篇详情：

```bash
# 基础详情
python scripts/cli.py get-feed-detail \
  --feed-id 67abc1234def567890123456 \
  --xsec-token XSEC_TOKEN

# 加载全部评论
python scripts/cli.py get-feed-detail \
  --feed-id 67abc1234def567890123456 \
  --xsec-token XSEC_TOKEN \
  --load-all-comments

# 加载全部评论（展开子评论）
python scripts/cli.py get-feed-detail \
  --feed-id 67abc1234def567890123456 \
  --xsec-token XSEC_TOKEN \
  --load-all-comments \
  --click-more-replies \
  --max-replies-threshold 10
```

### 获取用户主页

```bash
python scripts/cli.py user-profile \
  --user-id USER_ID \
  --xsec-token XSEC_TOKEN
```

输出包含：用户基本信息、粉丝/关注数、笔记列表。

## 结果呈现

搜索结果应按以下格式呈现给用户：

1. **笔记列表**：每条笔记展示标题、作者、互动数据。
2. **详情内容**：完整的笔记正文、图片、评论。
3. **用户资料**：基本信息 + 代表作列表。
4. **数据表格**：使用 markdown 表格展示关键指标。

## 失败处理

- **未登录**：提示用户先执行登录（参考 xhs-auth）。
- **搜索无结果**：建议更换关键词或调整筛选条件。
- **笔记不可访问**：可能是私密笔记或已删除，提示用户。
- **用户主页不可访问**：用户可能已注销或设置隐私。
