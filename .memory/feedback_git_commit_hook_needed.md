---
name: feedback_git_commit_hook_needed
description: git plugin PreToolUse hook 拦截 Bash(git add/commit) 重定向 /git:commit；放行
  `git add … && git-agent commit` 链式 + GIT_SKILL_FALLBACK=1 逃生标记
type: feedback
---

git plugin 的 PreToolUse hook 在工具层硬性拦截 `git add`/`git commit`，重定向到 `/git:commit` skill。

**Why:** Claude Code 系统提示内建了完整的多步 git commit 流程（status → diff → log → add → commit），优先级高于 CLAUDE.md 的单行指令。没有 hook，AI 会走内建流程而不是 /git:commit skill。

**How to apply:**
- 用户要求 commit 时，始终通过 Skill tool 调用 `/git:commit`，不要回退到 `git add && git commit`
- 放行形态只有两种：`git add … && git-agent commit` 单命令链式，或 skill 内 fallback 的 `GIT_SKILL_FALLBACK=1` 前缀
- 改 hook 的拦截范围时，务必同时跑 should-deny + should-pass 两条路径
- deny 用 exit 0 + stdout JSON，非 exit 2 + stderr
- 改 hook schema 前用 claude-code-guide agent 核对当前 API
- git-agent 二进制: `/Users/FradSer/.go/bin/git-agent`；源码: `~/Developer/FradSer/git-agent/git-agent-cli/`
- 关键 flags: `--intent`, `--co-author`, `--free`, `--no-stage`, `--dry-run`, `--amend`
- planner 超时加 `--free` 走内嵌凭证绕过 config endpoint，不要降级到手写 commit