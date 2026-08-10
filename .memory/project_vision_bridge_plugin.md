---
name: project_vision_bridge_plugin
description: vision 插件——移除代理改为 hook+describe；粘贴截图统一用网关视觉模型，代理方案已否决（部署模型与用户多上游玩错配）
type: project
---

`dotclaude/vision` 插件（原名 vb → vision → 脚本统一 vision_*）让非视觉模型（deepseek 系）能"看"图片文件。

**架构（2026-08-09 定稿）：**
- **已移除透明本地代理**（`scripts/vision_proxy.py` 的 serve/start/stop/status + `hooks/ensure_proxy.py` SessionStart hook + `ANTHROPIC_BASE_URL` 改写 + `blockedModels`）。原因：用户确认不需要"粘贴截图给 deepseek 自动看图"，且代理要求 env 改写 + 常驻进程。非视觉模型无法收粘贴截图（hook 看不到 image block），需视觉模型或 `describe <path>`。
- **现行能力（两个入口共享一套 vision.json + describe 引擎）：**
  1. **UserPromptSubmit hook**（`hooks/bridge_file_paths.py`）：自动描述文本里的图片文件路径，注入 additionalContext。
  2. **`scripts/vision_proxy.py` CLI**：`describe <path>` 按需描述、`doctor` 校验视觉配置 + 端点（逐模型探测 fallback 链）。
- **独立视觉服务商**：`baseUrl` + `apiKey` 指向 OpenAI 兼容端点，绝不复用 `ANTHROPIC_AUTH_TOKEN`/`ANTHROPIC_API_KEY`。
- **三层 `vision.json` 配置**：全局 `~/.claude/vision.json` → 项目 `.claude/vision.json` → 本地 `.claude/vision.local.json`（gitignored）。`${VAR}` 环境引用支持。
- **视觉模型降级链**：`model` 逗号分隔，网关视觉模型会 `model_cooldown`，自动换下一个。默认 `gemini-3.1-flash-image,gemini-3-flash-agent`。
- 本机实测：`OPENAI_BASE_URL=10.10.0.195:8317/v1` + `OPENAI_API_KEY` 是有效视觉服务商组合；4x4 微型 PNG 会被 Google 拒。

**doctor 修复（本次发现并修）：** 旧 doctor 用整条逗号拼接的模型链当单个 model 名探测 → 网关 400。现改为逐模型探测，任一 200 即通过。

**已知边界：** 粘贴截图（image block）不受 hook 覆盖——非视觉模型收不到。`~/.vb/` 旧代理遗留已删。

**粘贴截图的最终决策（勿再提议恢复代理）：** 用户网关（10.10.0.195:8317）上有多个原生多模态模型（gemini/gpt/glm 系）。粘贴截图场景直接用视觉模型原生看图；deepseek 只用于纯文本/代码。代理方案经通用性分析后否决：协议层通用（Anthropic 生态标准桥接），但部署模型（单固定 upstream + ANTHROPIC_BASE_URL env 改写 + 常驻进程）与用户环境错配——多上游（kimi/glm/doubao 官方等）、claude() 包装函数会强制 export ANTHROPIC_BASE_URL、多客户端（opencode 等）单点不覆盖。通用性排序：换视觉模型 > 文件路径 hook > 代理。若未来用户坚持"必须 deepseek 看粘贴截图"，唯一手段才是恢复代理（见 git 历史）。

**Why/How：** 模型冷却现象反复出现，是网关 provider 侧状态，非插件 bug。降级链 + `doctor` 诊断是解法。相关：[[reference_git_coauthor_allowlist]]（本机网关凭据）、[[feedback_verify_problem_real]]（冷却 vs 代码 bug 区分）。
