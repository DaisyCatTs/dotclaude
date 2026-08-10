---
name: project_reviewpr_pr22_cycle
description: review-fix 循环收敛教训——改 bash arg-parse 必测 4 路、--paginate 对称加、macOS bash
  3.2 无关联数组
type: project
---

PR #22（review-pr skill + json trope prefs）经 9 轮 bot review-fix 循环才收敛（gemini-code-assist / devin-ai / greptile 三家 18 条评论，16 fix / 2 reject）。教训是可迁移的 bash/API 规则，而非那次 PR 的流水账：

**How to apply:**
- **改 bash arg-parse 后必测 4 路**：env-only / flag-only / env+flag / 缺值。第 6 轮的 env-precedence 修复在 `set -u` 下访问 `$2`（在 `shift 2` 之前）崩溃 + 默认值短路使 `--interval` 变死代码——两个回归各花一轮才被 bot 抓到
- **加 `--paginate` 要对称加到所有同类 API 调用**：给 reviews 加了但漏了 issue/inline 两个 comment 调用，`since` 前进后 >30 条历史评论被永久截断丢失
- **macOS /bin/bash 是 3.2，无关联数组**（`declare -A` 静默失败）——CI dedup 用 newline-delimited string map；check 名含空格不能用 space-delimited
- **收敛判断**：核心逻辑闭环 + 边际收益递减时主动停手，继续追新发现可能在修边缘代码时引入新 bug

关联 [[feedback_self_audit_caught_my_bugs]]、[[feedback_verification]]、[[project_reviewpr_closeout]]
