---
name: project_gitflow_plugin
description: gitflow 插件建在 git-flow-next 之上，非经典 nvie/avh git-flow；finish 停 main/不自动
  push
type: project
---

`gitflow` 插件（commit scope `gitflow`，6 个 skill：feature/release/hotfix 的 start/finish）建在 **git-flow-next**（git-flow.sh / gittower，Go 重写版，brew `gittower/tap/git-flow-next`）之上——**不是**经典 nvie/avh git-flow，flag 与行为有别。

**git-flow-next 关键事实：**
- 默认主分支是 `main`，默认前缀 `feature/`/`release/`/`hotfix/`
- `release finish`/`hotfix finish` 完成后停在 `main`（develop 经 `AutoUpdate=true` 自动回并）；`feature finish` 回到 `develop`
- **finish 不自动 push**——脚本必须手动 `git push origin main develop --tags`
- finish 默认删除分支（本地+远程，`--keep` 保留）
- `release/hotfix finish [name]` 的 name 是可选位置参数（省略则从当前分支推断）

**关键约束：**
- 6 个 skill 纯指令、无脚本，每个启一个 general-purpose agent 执行
- 所有 CRITICAL 规则：clean tree 检查、finish 分支类型匹配、start-hotfix/release 的 semver 断言
- 提交走 `git add … && git-agent commit --no-stage …` 链式命令（git hook 放行形态）
- 不要硬编码模型版本——从运行时身份推导

**How to apply:** 改本插件前按 git-flow-next（非经典 gitflow）核对；升级 git-flow-next 后重验 finish 落点/flag。

关联：[[feedback_git_commit_hook_needed]]、[[feedback_skill_level_enforcement]]