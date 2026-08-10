---
name: reference_anthropic_harness_blog
description: Anthropic harness 设计博文核心原则：context reset、GAN 评估器、binary PASS/FAIL、sprint
  contracts、假设测试、simplify-don't-add
type: reference
---

Blog: https://www.anthropic.com/engineering/harness-design-long-running-apps

**Why:** eval harness 和 superpowers 架构演化的主要外部参考。[[project_active_design_work]] 和 [[project_superpowers_hooks]] 都引用它。

**How to apply:** 修改 eval harness 或 superpowers 架构前复习这些原则。

## 核心原则

1. **Context resets > context compaction** — 模型随 context 填充失去连贯性，干净切换 + 结构化摘要优于就地压缩
2. **GAN 式分离** — Generator 产出，独立 Evaluator 批评。调优独立 evaluator 的怀疑倾向比让 generator 自我批评更容易
3. **Binary PASS/FAIL** — 具体证据，非主观 1-5 评分。`FAIL -- [具体技术原因]`
4. **Sprint contracts 是承重件** — 实现前的显式范围 + 成功标准协议
5. **假设测试** — 每个 harness 组件都编码关于模型局限的假设。模型改进时逐一测试哪些仍承重，剥离开销
6. **Evaluator 价值取决于任务** — 超出模型基线能力时必要，否则是开销。Opus 4.6 将 evaluator 从强制 per-sprint 改为战略性 end-stage
7. **校准循环** — Few-shot 示例 + 迭代对齐。读 evaluator 日志，找与人类判断的分歧，更新 prompt

## 模型演化教训

Opus 4.6 消除了 context reset 和 sprint 分解的需要。Evaluator 从强制变为战略。成本：$124-200 多小时运行 vs 单 agent 20 分钟 $9。

**对 superpowers 的启示：** 模型升级时重新审视 harness。Simplify, don't only add — 这正是大规模拆除（删 SessionStart hook、停用旧 lib）的思想基础。
