---
name: project_superpowers_upstream_lessons
description: 上游 obra/superpowers v6.0.x-v6.1.1 设计约束与思想；本地已吸收 8 条 Tier 1-2 候选
type: project
---

本地是上游 obra/superpowers 的 curated fork，不引入上游 SDD / brainstorm 可视化伴侣 / 多 harness 体系。

**已吸收的 3 条约束（v6.0.x）：**
1. subagent 产物目录不写 `.git/`——放工作树内自忽略目录
2. 每次 dispatch subagent 必须显式声明 model（sonnet 默认 / opus 仅难推理 / haiku 机械扫）
3. 禁止 controller 让 reviewer 忽略 finding 或预标 severity

**v3.7.0 吸收的 Tier 1-2 候选（8 条）：**
1. implementer 四状态协议（DONE/DONE_WITH_CONCERNS/NEEDS_CONTEXT/BLOCKED）+ BLOCKED 分诊
2. 任务级 durable progress ledger（task-ledger.jsonl，防重派已完成任务）
3. Pre-Flight 计划矛盾扫描（mandate vs 评审规则冲突）
4. review-package 的 BASE 用派发前记录的 commit，非 `HEAD~1`
5. BDD 反合理化段（delete means delete / tests-after 证明不了任何东西 / Verify RED 强制）+ testing-anti-patterns.md
6. 禁用并行场景清单（失败相互关联/探索式调试/同文件冲突）
7. worktree gitignore 持久化（`.claude/worktrees/` 入仓库 `.gitignore`）
8. evaluator 校准补充（不信 implementer 自评 rationale；REWORK 只派一个 fixer 带完整清单）

**本地领先上游的点：** retrospective 自进化 checklist、evaluator 独立 agent + 二元裁决、docs-index + memory 层、正式 pytest 套件、/goal 编排（SessionStart hook 已删——见 [[project_superpowers_hooks]]）

关联：[[project_superpowers_hooks]]、[[project_active_design_work]]