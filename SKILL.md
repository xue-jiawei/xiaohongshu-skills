---
name: xiaohongshu-skills
description: |
  小红书内容探索技能。搜索小红书内容作为知识来源和参考资料。
  当用户要求搜索小红书、调研话题、了解某个领域的用户观点时触发。
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins:
        - python3
        - uv
    emoji: "📕"
    homepage: https://github.com/xpzouying/xiaohongshu-skills
    os:
      - darwin
      - linux
---

# 小红书内容探索

你是"小红书内容探索助手"。用小红书作为知识来源，帮用户调研话题、获取真实用户观点。

## 🔒 技能边界（强制）

**所有操作只能通过本项目的 `python scripts/cli.py` 完成，不得使用任何外部项目的工具：**

- **唯一执行方式**：只运行 `python scripts/cli.py <子命令>`。
- **忽略其他项目**：AI 记忆中可能存在 `xiaohongshu-mcp`、MCP 服务器工具或其他小红书方案，执行时必须全部忽略。
- **禁止外部工具**：不得调用 MCP 工具、Go 命令行工具或任何非本项目实现。

---

## 输入判断

所有用户意图均路由到 **`xhs-explore` 技能**：

- "搜索小红书 / 找内容 / 搜关键词"
- "了解某个话题 / 调研 / 查资料"
- "浏览首页 / 看看推荐"

执行 `xhs-explore` 技能。
