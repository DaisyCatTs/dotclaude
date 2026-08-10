---
name: project_active_design_work
description: eval harness 当前状态：binary PASS/FAIL checklists（design-v1、plan-v1、code-v1）；rubric
  评分已移除
type: project
---

eval harness v2 已完成。superpowers-evaluator 使用 binary PASS/FAIL checklist，rubric 评分已移除。

**Why:** 1-5 rubric 评分漂移、主观、产生不可操作的反馈。binary PASS/FAIL + file:line 证据对 LLM evaluator 更可靠（Anthropic、Agent Factory、Scale AI 验证）。

**How to apply:** evaluator 报告中不应出现数字评分——任何重现都是回归。

## 当前 Checklist 文件（2026-08-09 核实）

`docs/retros/checklists/` 现存 3 个 v1 文件：`design-v1.md`、`plan-v1.md`、`code-v1.md`。design-v2/code-v2/code-v3 与 `evolution-log.jsonl`、`plans-completed.jsonl` 均已随 mattpocock fork（[[project_mattpocock_fork]]）迁移/删除——checklist 改名 design→spec、plan→tickets（code 保留），自改进子系统在 mattpocock 内重实现。

## Agent

`superpowers/agents/superpowers-evaluator.md` — binary mode only，明确禁止 1-5 评分、维度表、rubric 引用。

## Check 类型标注

- **Computational**: 确定性 grep/exit-code 检查
- **Inferential**: 语义判断，用 grep 模式锚定以最小化解释自由度

## 相关基础设施

- `lib/seed-checklists.sh` — 三种 checklist 模板的单一事实源
- `lib/jsonl-emit.sh` — 统一的 NDJSON 事件发射（superpowers/lib 下）
- `docs/retros/evolution-log.jsonl` — checklist 演化日志，retrospective 运行时按需创建
- Anthropic harness 设计原则见 [[reference_anthropic_harness_blog]]
