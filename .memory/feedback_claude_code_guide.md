---
name: feedback_claude_code_guide
description: 插件改动前先用 claude-code-guide agent 验证当前 Claude Code API 和模式
type: feedback
---

修改插件 skill、agent、hook 或 tool 引用前，先 spawn `claude-code-guide` agent 验证当前正确的模式。

**Why:** Claude Code 插件系统演化快。依赖过时知识会导致使用已废弃 API（如 `TodoWrite` 而非 `TaskCreate`）、错误的 tool 模式，或遗漏新能力。

**How to apply:**
- 修改前 spawn `claude-code-guide` agent 验证当前允许的工具语法、frontmatter 字段等
- 结合领域研究（如 `code-context:context-researcher` 查外部最佳实践）做综合决策
