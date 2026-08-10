---
name: feedback_pi_file_edit_output
description: pi 的产出是文件编辑而不是 stdout 文本，带长 --append-system-prompt 时 stdout 为空
type: feedback
---

pi（dev/pi coding harness）的真实产出是文件编辑，不是 stdout 文本。当 `--append-system-prompt` 携带大量上下文时，pi 的 stdout 经常保持为空，看起来像卡死但实际上正在修改文件。

**Why:** 之前用 Monitor 执行 pi -p，Monitor 按 stdout 事件触发 + 300s 超时。pi 思考时无输出 + 长时间运行 + stdout 为空 → 必然超时无结果。用户误以为失败，直到把命令写进脚本后台运行、检查 `git diff --stat` 才发现文件已被修改。

**How to apply:**
- 永远不要用 Monitor 跑 pi（Monitor 是给 `tail -f` 这类持续事件流的）
- 用 `Bash` + `run_in_background`，**不要 shell timeout**（任务可能很重，需要自然完成）
- **不要传 `@.` 或任何文件引用** — pi 不支持目录路径（EISDIR），pi 自己有 `read`/`grep`/`find`/`ls` 工具可以探索代码库；只传 task description 即可
- 仅当用户明确指定文件时才传 `@filepath`
- pi 完成后优先检查 `git diff --stat`，不是 stdout
- SKILL.md 的 allowed-tools 必须放行 git 和 jq，否则无法收集上下文和检查结果