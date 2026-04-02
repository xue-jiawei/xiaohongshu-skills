---
name: xhs-explore
description: |
  小红书知识探索技能。搜索小红书内容作为参考资料和知识来源。
  当用户需要了解某个话题、调研某个领域、寻找灵感或参考时触发。
version: 2.1.0
metadata:
  openclaw:
    requires:
      bins:
        - python3
        - uv
    emoji: "🔍"
    os:
      - darwin
      - linux
---

# 小红书知识探索

用小红书作为 **知识库 / 参考源**，提取真实用户经验和观点。

## 技能边界

只通过 `uv run python scripts/cli.py` 执行，忽略其他任何小红书工具或 MCP 服务。

使用以下三个命令实现完整的探索工作流：

| 命令 | 用途 | 场景 |
|------|------|------|
| `search-and-fetch` | 搜索关键词 + 批量获取详情 | 有明确话题时使用（**高性能**，并发获取） |
| `list-and-fetch` | 首页推荐 + 批量获取详情 | 无明确话题时使用（**高性能**，并发获取） |
| `user-profile` | 获取特定用户主页 + 全部帖子 | 深入特定发布者内容（找到有价值的内容源） |

---

## 账号选择（前置步骤）

```bash
uv run python scripts/cli.py list-accounts
```

- 0 个命名账号：使用默认账号（后续命令不加 `--account`）
- 1 个命名账号：加 `--account <名称>` 执行
- 多个命名账号：询问用户选择，全程固定该账号

---

## 命令参数说明

### search-and-fetch

```
uv run python scripts/cli.py search-and-fetch [args]
```

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `--keyword` | str | ✅ | — | 搜索关键词 |
| `--top-n` | int | | 5 | 获取前 N 条笔记的详情 |
| `--sort-by` | str | | 综合 | 排序方式：`综合` \| `最新` \| `最多点赞` \| `最多评论` \| `最多收藏` |
| `--note-type` | str | | 不限 | 内容类型：`不限` \| `图文` \| `视频` |
| `--publish-time` | str | | 不限 | 发布时间：`不限` \| `一天内` \| `一周内` \| `半年内` |
| `--search-scope` | str | | 不限 | 范围：`不限` \| `已看过` \| `未看过` \| `已关注` |
| `--location` | str | | 不限 | 地理：`不限` \| `同城` \| `附近` |
| `--account` | str | | 默认账号 | 账号名称（多账号时使用） |

**注：** 搜索命令自动运行在无头模式，无需添加 `--headless` 参数

**示例：**

```bash
# 基础搜索（获取前 5 条的详情）
uv run python scripts/cli.py search-and-fetch \
  --keyword "春招面试" \
  --top-n 5

# 搜索最新图文，过去一周内
uv run python scripts/cli.py search-and-fetch \
  --keyword "春招面试" \
  --top-n 5 \
  --sort-by 最新 \
  --note-type 图文 \
  --publish-time 一周内

# 完整流程：搜索 → 阅读详情 → 进入特定用户主页
# 1. 搜索获取列表
uv run python scripts/cli.py search-and-fetch \
  --keyword "春招面试" \
  --top-n 10
  # 获取 output_dir 和 details 列表，内含各帖子的 user_id, xsec_token

# 2. 阅读 {output_dir}/feed_{feed_id}.json 了解内容

# 3. 如发现有价值的发布者，深入探索其主页
uv run python scripts/cli.py user-profile \
  --user-id "发布者ID" \
  --xsec-token "从搜索结果中获取"
  # 获取该发布者的全部笔记和互动信息
```

---

### list-and-fetch

```
uv run python scripts/cli.py list-and-fetch [args]
```

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `--top-n` | int | | 5 | 获取前 N 条推荐笔记的详情 |
| `--account` | str | | 默认账号 | 账号名称（多账号时使用） |

**注：** 推荐列表命令自动运行在无头模式，无需添加 `--headless` 参数

**示例：**

```bash
uv run python scripts/cli.py list-and-fetch \
  --top-n 5
```

---

### user-profile

```
uv run python scripts/cli.py user-profile [args]
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `--user-id` | str | ✅ | 用户 ID（可从 search/list 结果中的 `user_id` 获取） |
| `--xsec-token` | str | ✅ | xsec_token（可从 search/list 结果中的 `xsec_token` 获取） |
| `--account` | str | | 账号名称（多账号时使用） |

**示例：**

```bash
# 从搜索结果中找到感兴趣的发布者，进一步探索其主页
uv run python scripts/cli.py user-profile \
  --user-id BIGe_W2CAAAA \
  --xsec-token AQDSSRGblVVcRAH_o2R8-w
```

**输出包含：**
- 用户基本信息（昵称、粉丝数、简介等）
- 用户的全部笔记（批量获取）
- 用户的互动统计

---

## 工作流程（3 步探索）

### 第 1 步：搜索或浏览

根据用户需求选择：

- **有明确话题** → `search-and-fetch`（搜索关键词）
- **无明确话题** → `list-and-fetch`（首页推荐，适合发现灵感）

*搜索和推荐命令自动运行在无头模式（性能优化）*

### 第 2 步：解析搜索结果

从 manifest 中获取：
- `output_dir` — 详情 JSON 所在目录
- `details` 列表 — 每条帖子的 `feed_id`, `xsec_token`, `user_id` 等

用 Read 工具读取 `{output_dir}/feed_{feed_id}.json` 获取完整内容。

### 第 3 步：深入探索（可选）

如果发现有价值的发布者，可进一步探索其主页：

```bash
uv run python scripts/cli.py user-profile \
  --user-id <用户ID> \
  --xsec-token <xsec_token> \
  --headless
```

*输出用户信息和该用户的全部帖子列表，继续提取核心观点。*

### 综合呈现

1. 读取所有详情 JSON
2. 提炼核心观点、关键观点、评论中的有价值观点
3. **不要**原样输出 JSON，改用结构化 markdown（标题、要点、表格）
4. 标注来源（哪篇笔记 / 哪个用户提到的）

---

## 结果呈现规范

### ✅ 必须做

- 提取各笔记的核心观点和关键信息
- 归纳共同趋势或不同观点
- 用 markdown 结构化呈现：标题、要点、表格、列表等
- 标注来源：`(来自笔记 ID: xxx / 作者: xxx)`
- 评论中有价值的观点一并提取（如有深度回复）

### ❌ 禁止做

- **不要**原样输出 JSON
- **不要**列出所有原始数据
- **不要**忽略用户主页信息（如已获取）

### 示例格式

```markdown
## 关键观点总结

### 观点 1：XXX
- 来自笔记 ID: abc123 / 作者: 某发布者
- 更多细节...

### 共同点 / 差异

| 发布者 | 观点 | 点赞数 |
|---|---|---|
| 用户A | 描述A | 1.2K |
| 用户B | 描述B | 800 |

### 深度评论中的洞见
- "用户C 的评论指出..." (出现在笔记 def456 下)
```

---

## 失败处理

| 场景 | 处理方式 |
|------|------|
| **未登录** | 提示用户先执行登录（参考 xhs-auth 技能） |
| **无搜索结果** | 建议换关键词、调整排序方式或放宽时间/内容类型筛选 |
| **笔记不可访问** | 跳过，继续处理其他结果 |
| **用户主页加载失败** | 确认 user_id 和 xsec_token 正确，或提示用户账号权限问题 |

---

## 性能优化 (重要)

- **并发获取** — `search-and-fetch` 和 `list-and-fetch` 使用批量并发获取详情，比逐个获取快 3-5 倍
- **无头模式** — 搜索和推荐命令自动运行在无头模式，避免浏览器 UI 开销
- **选择合适的 top-n** — 5-20 条通常足够，过多会延长执行时间
- **限制查询范围** — 利用 `--sort-by`, `--note-type`, `--publish-time` 等过滤器缩小搜索范围

---

## 工作流提示

**理想探索路径：**
```
明确话题 
  ↓
search-and-fetch (关键词搜索，--top-n 5-10)
  ↓
分析搜索结果 → 找到高质量发布者
  ↓
user-profile (深入该发布者，了解其全部内容)
  ↓
综合整理，提炼核心观点
```

**无明确话题的探索：**
```
list-and-fetch (首页推荐，--top-n 10)
  ↓
发现感兴趣的内容方向
  ↓
根据发现的方向，回到 search-and-fetch 进一步细化搜索
  ↓
或进入特定发布者主页深度了解
```
