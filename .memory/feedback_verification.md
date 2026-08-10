---
name: feedback_verification
description: 报告前必须验证产物（跑代码、测交互、检查输出）；行为偏好，不再有 hook 强制
type: feedback
---

Always verify work before reporting completion.

**Why:** 防止将不完整或未测试的产物交还给用户。

**How to apply:**
- 跑自己写/改的代码，检查输出
- Web app：打开页面，点击流程，验证渲染和交互
- 用真实或代表性输入测试
- 模拟边界情况
- 纯讨论/规划/研究等无可验证产出的任务可跳过

**Note:** 此规则是行为偏好，不是 hook-enforced gate——`<verified>` Stop-hook 强制与 `/need-vet` 机制已移除，Stop-hook 续跑循环已删除。不输出 verification tag。
