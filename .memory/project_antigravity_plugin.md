---
name: project_antigravity_plugin
description: antigravity 插件——委托 Google Gemini Managed Agents 的桥接插件；实测 API 事实与已知缺陷清单
type: project
---

`antigravity` 插件（active，commit scope `ag`）：Bridge 型，把任务委托给 Google Gemini Managed Agents 远程沙箱。两个 slash command：`/antigravity:delegate`、`/antigravity:research`。机制：`scripts/antigravity.py`（uv + PEP 723 内联 `google-genai`）经 Bash 调用，detached worker + `wait` 子命令轮询状态文件，skill 用 Monitor 等待。

**实测 API 事实（与调研文档多处不符）：**
- `background` 按 agent 相反：deep-research agent 要求 `background=True`（异步轮询）；antigravity agent 拒绝 `background`（同步阻塞）
- `environment.network` 枚举是 `"disabled" | {allowlist:[...]}`。省略该字段 = 开放
- worker 里 `get()` 不传 timeout 会被服务端长轮询阻塞 → 必须 `get(timeout=60)` + 重试
- 真实 agent ID：`antigravity-preview-05-2026`、`deep-research-preview-04-2026`、`deep-research-max-preview-04-2026`（`--max`）
- `Interaction.status` 是 7 值 Literal：活跃态 `in_progress`/`requires_action`；终态 `completed`/`failed`/`cancelled`/`incomplete`/`budget_exceeded`
- 当前 SDK 版本 2.16.0（pin 是 `>=1.55.0`）
- **`interactions.create()` 最近返回 401 `ACCESS_TOKEN_TYPE_UNSUPPORTED`**——改本插件前必须先确认上游还活着

**已知 HIGH 缺陷（2026-08-04 反思确认）：**
1. 无 liveness 检测——worker 被 kill -9/睡眠断电后 status 永远 "running"
2. `extract_result` 只取最后一个 model_output 段——长运行报告丢开头
3. Monitor `timeout_ms=900000` == `wait --timeout` 默认 900s，Monitor 先杀 wait → 超时行永不输出 → skill 的 timeout 分支是死代码
4. Monitor-re-arm 对 one-shot 事件是错误原语，2h run 需 8 次串行 re-arm

**How to apply:** 改本插件前先 live probe 确认上游活着并按实测事实核对；API 仍 Pre-GA，升级 google-genai 后需重验。修复清单按上面 HIGH 分组。

关联：[[feedback_verification]]、[[feedback_claude_code_guide]]