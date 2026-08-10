---
name: project_autoresearch_plugin
description: autoresearch 插件：ralph-loop Stop hook + 8 次 block 上限；混合引擎（顺序+ tournament）；worktree
  隔离
type: project
---

autoresearch 是 ralph-loop 插件：`hooks/stop-hook.sh` 用 `{"decision":"block","reason":<full prompt>}` 在每次 Stop 时把研究提示重新喂回，循环到自带 bound。

**关键外部约束：**
- Claude Code 在 Stop hook 连续 block `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` 次后强制结束回合（**默认 8**，设 `0` 禁用）
- 插件**无法自行设置该 env**——只能 setup 脚本检测并警告，让用户在 `.claude/settings.json` 的 `env` 块设 `"0"` 并重启会话
- 不要给 hook 加 `stop_hook_active` 早退守卫——那会在第一次 block 后就杀死故意的长循环

**混合引擎：**
- `/start "<目标>"` 唯一入口，自主推断契约（读目标+仓库 → 定 edit/评估器/方向/边界）
- 默认每轮廉价顺序改动；连续 K 轮（默认 3）无改进=陷入局部最优时，该轮升级为一次 tournament（GAN 锦标赛引擎，复用 `gan.mjs`）
- 动因：tournament ≈ 126k tokens/轮，所以只用在卡住时

**worktree 隔离：**
- `git worktree add .claude/worktrees/autoresearch-<tag> -b autoresearch/<tag>` 取代 `git checkout -b`
- 主 checkout/当前分支/脏树永不被触碰，脏主树也能启动
- 为何不用 `EnterWorktree` 工具：它跨 Stop-hook 循环/压缩的持久性未文档化，自治循环用插件自管 `git worktree` 更稳

**临时提交模型：**
- 循环不做真提交。keep 折叠进单个滚动 `autoresearch WIP (temporary)` scratch 提交
- discard 用 `git checkout -- <edit>`
- `results.tsv` 是唯一耐久记录
- 跑完 `git reset --soft <baseline_sha>` 折叠成未提交 diff，由人 review 后经 `/git:commit` 落地

**可插拔评估器：**
- `--check-cmd`（客观闸门，exit 0=过，硬过滤）
- `--score-cmd`（数值，按 direction 排）
- `--rubric`（GAN 专属，LLM 量规裁判）
- **抗刷分铁律：** `--rubric` 必须配 `--score-cmd` 或 `--check-cmd` 锚点

**已知陷阱：**
- `${CLAUDE_PLUGIN_ROOT}` 在 hook 重注入的提示词里不可用——setup 时把绝对路径烤进状态文件
- `set -euo pipefail` 下 `VAR="...$(cond && echo X)..."` 当 cond 假时 `$(...)` 返回 1 → 中止；必须 `$(cond && echo X || :)`
- 所有"程序"嵌在 `scripts/setup-autoresearch.sh` 的非引号 heredoc 里——改文案时禁止用反引号或 `$(...)`，否则生成状态文件时会被执行

关联：[[feedback_claude_code_guide]]、[[reference_anthropic_harness_blog]]