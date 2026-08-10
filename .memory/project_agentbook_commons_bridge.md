---
name: project_agentbook_commons_bridge
description: commons-bridge 设计已 PASS 但无 plan 无代码；要点存 docs/orphaned-designs.md；重启时改走
  mattpocock 流程
type: project
---

agentbook（`/Users/FradSer/Developer/FradSer/agentbook`，"public debug-knowledge commons for AI coding agents"）接入 dotclaude 的 commons-bridge 设计已 PASS（6 轮 evaluator 往返），但从未写实施计划、零代码实现。

**Why:** 完整设计要点（独立插件 + `plugin.json "dependencies"` 声明、recall/publish 双 skill、outward publish 四条件门、3 个消费触点）已沉淀在仓库内 `docs/orphaned-designs.md` 的 agentbook 段——它是权威索引，`docs/plans/` 已整体清空，重启时据此重写，不要重复调研。

**How to apply:**
- 重启时改走 mattpocock 流程（[[project_mattpocock_fork]]），不再走已不可靠的 superpowers writing-plans 路径
- 设计细节点位在 `docs/orphaned-designs.md`，本 memory 只留状态指针

关联：[[project_mattpocock_fork]]、[[project_superpowers_hooks]]、[[project_superpowers_upstream_lessons]]
