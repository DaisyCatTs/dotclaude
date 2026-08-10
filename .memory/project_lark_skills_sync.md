---
name: project_lark_skills_sync
description: lark/skills/ 是 larksuite/cli GitHub skills/ 的 vendored 镜像；lark-cli 升级时需重新同步
type: project
---

`lark/skills/` 是上游 [larksuite/cli](https://github.com/larksuite/cli) 仓库 `skills/`（main 分支）的 vendored 镜像（dotcodex 对应 `plugins/lark/skills/lark/`，嵌套深一层）。

**同步源 = GitHub main**，不是本地 `~/.agents/skills/lark-*`。2026-05-25 决策。

**同步机制：** `bash lark/scripts/sync-lark.sh [--check|--force]`（共享工具 `tools/skill-sync/denest.py` + `gen-index.py`；dotcodex 版在 `plugins/lark/scripts/`）。脚本 sparse-checkout 克隆 GitHub `skills/` 后整体镜像，删除上游已移除的目录，保留本地 `SKILL.md`（路由表）；`SYNC.md` 位于插件根（`lark/SYNC.md`），不在镜像树内。`SKILL.md` 的 Sub-skill Index 表由 `gen-index.py` 按子 skill frontmatter 重生成，脚本不覆盖其余部分。

**版本标记：** `SYNC.md` 头部三字段由脚本每次同步自动刷新——Last sync / lark-cli version / Synced commit（27 个 lark-* 目录）。

**触发时机：lark-cli 更新时重新同步。**

**踩坑：** 脚本原 `SCRIPT_DIR="$(cd … && pwd)"` 在本机 shell（`cd` 被改写成会回显路径）下会算出带换行的重复路径导致失败；已加 `>/dev/null 2>&1` 静默 cd 修复。

frontend 插件已于 2026-07-23 删除（commit `b88eeba`），其 `frontend/scripts/` 同步模式不再适用——此前曾与 lark 共用同一套模式。
