---
name: feedback_verify_problem_real
description: 遇到问题（hook 阻塞/报错）时先验证问题是否真实存在：简单直接判，复杂起独立 subagent
type: feedback
---

遇到报错、hook 阻塞或其他「问题」时，先验证问题是否真实存在，再采取行动。验证分两级：
1. **简单**：自行直接判断（如 `gh pr view --json state,mergedAt` 一次调用能定性）
2. **复杂/模糊**：启动**独立上下文**的 subagent 去验证，主上下文有沉没成本偏见（自写代码/自跑流程），不能自己定性

**Why:** 2026-08-04 用户为 closeout Stop hook 提出此要求。hook 只认状态文件，不知道 closeout 是否其实已解决（ask 已问过、总结已发、PR 已合并，只是 clear 没跑）——「问题」可能是 stale 状态的假警报。误信假警报会导致重复询问/重复执行。

**How to apply:** 机制性守卫（hook 消息）与技能文档（closeout.md "When the hook fires"）都内置此指令；平时遇到任何报错/拦截也适用。验证为 stale 就清除状态正常结束，不重复动作。关联 [[feedback_verification]]、[[feedback_self_audit_caught_my_bugs]]、[[project_reviewpr_closeout]]。
