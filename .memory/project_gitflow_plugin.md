---
name: project_gitflow_plugin
description: gitflow 功能已并入 git 插件（6 个 start/finish skill）；建在 git-flow-next 之上，finish 停
  main/不自动 push
type: project
---

独立 gitflow 插件已于 2026-08-02 移除（commit `12055fc4 refactor: restructure marketplace plugins`），gitflow 的 6 个 skill 并入 `git` 插件：`git/skills/{start,finish}-{feature,release,hotfix}`。无独立 commit scope——相关提交走 `git` scope。

6 个 skill 建在 **git-flow-next**（git-flow.sh / gittower，Go 重写版，brew `gittower/tap/git-flow-next`）之上——**不是**经典 nvie/avh git-flow，flag 与行为有别。

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

**How to apply:** 改 git 插件内 gitflow skill 前按 git-flow-next（非经典 gitflow）核对；升级 git-flow-next 后重验 finish 落点/flag。

关联：[[feedback_git_commit_hook_needed]]、[[feedback_skill_level_enforcement]]
