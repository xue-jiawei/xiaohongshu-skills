---
name: xhs-explore
description: |
  小红书知识探索技能。搜索小红书内容作为参考资料和知识来源。
  当用户需要了解某个话题、调研某个领域、寻找灵感或参考时触发。
version: 2.0.0
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

只通过 `python scripts/cli.py` 执行，忽略其他任何小红书工具或 MCP 服务。

只使用以下两个命令：

| 命令 | 用途 |
|------|------|
| `search-and-fetch` | 搜索关键词 + 批量获取详情（有明确话题时使用） |
| `list-and-fetch` | 首页推荐 + 批量获取详情（无明确话题时使用） |

---

## 账号选择（前置步骤）

```bash
python scripts/cli.py list-accounts
```

- 0 个命名账号：使用默认账号（后续命令不加 `--account`）
- 1 个命名账号：加 `--account <名称>` 执行
- 多个命名账号：询问用户选择，全程固定该账号

---

## 命令参数说明

### search-and-fetch

```
python scripts/cli.py search-and-fetch [args]
```

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `--keyword` | str | ✅ | — | 搜索关键词 |
| `--top-n` | int | | 5 | 获取前 N 条笔记的详情 |
| `--headless` | flag | | false | **始终加上**，不弹出浏览器窗口 |
| `--sort-by` | str | | 综合 | 排序方式：`综合` \| `最新` \| `最多点赞` \| `最多评论` \| `最多收藏` |
| `--note-type` | str | | 不限 | 内容类型：`不限` \| `图文` \| `视频` |
| `--publish-time` | str | | 不限 | 发布时间：`不限` \| `一天内` \| `一周内` \| `半年内` |
| `--search-scope` | str | | 不限 | 范围：`不限` \| `已看过` \| `未看过` \| `已关注` |
| `--location` | str | | 不限 | 地理：`不限` \| `同城` \| `附近` |
| `--account` | str | | 默认账号 | 账号名称（多账号时使用） |

**示例：**

```bash
# 基础搜索
python scripts/cli.py search-and-fetch \
  --keyword "春招面试" \
  --top-n 5 \
  --headless

# 搜索最新图文，过去一周内
python scripts/cli.py search-and-fetch \
  --keyword "春招面试" \
  --top-n 5 \
  --headless \
  --sort-by 最新 \
  --note-type 图文 \
  --publish-time 一周内
```

---

### list-and-fetch

```
python scripts/cli.py list-and-fetch [args]
```

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `--top-n` | int | | 5 | 获取前 N 条推荐笔记的详情 |
| `--headless` | flag | | false | **始终加上**，不弹出浏览器窗口 |
| `--account` | str | | 默认账号 | 账号名称（多账号时使用） |

**示例：**

```bash
python scripts/cli.py list-and-fetch \
  --top-n 5 \
  --headless
```

---

## 工作流程

1. **理解意图** — 从用户描述中提取关键词和筛选需求
2. **选参数** — 根据意图决定 keyword / sort-by / note-type / publish-time 等
3. **执行命令** — 始终加 `--headless`，output-dir 留空自动生成
4. **读取结果** — stdout 输出 manifest JSON，包含 `output_dir` 和 `details` 列表
5. **读取详情** — 用 Read 工具读取 `{output_dir}/feed_{feed_id}.json`
6. **综合呈现** — 提炼核心观点，结构化 markdown 输出，不要原样输出 JSON

---

## 结果呈现规范

- **不要**原样输出 JSON
- 提取各笔记的核心观点和关键信息
- 归纳共同趋势或不同观点
- 用 markdown 结构化呈现（标题、要点、表格）
- 标注来源（哪篇笔记提到的）
- 评论中有价值的观点一并提取

---

## 失败处理

- **未登录**：提示用户先执行登录（参考 xhs-auth 技能）
- **无搜索结果**：建议换关键词或放宽筛选条件
- **笔记不可访问**：跳过，继续处理其他结果
