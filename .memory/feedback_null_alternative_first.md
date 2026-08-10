---
name: feedback_null_alternative_first
description: 给插件加新交付面（skill/hook/命令/agent）前，sprint contract 必须先论证 null alternative：现有
  references/*.md 扩展 + 平台原生能力覆盖
type: feedback
---

给插件新增任何"交付面"（新 skill、新 hook、新命令、新 agent——任何带独立触发/加载机制的东西）之前，Phase 1 sprint contract 的 "Alternatives considered" 必须包含 **null alternative**：(a) 扩展现有无触发面的 `references/*.md`（superpowers 已有惯例：`goal-wrapper.md`、`workflow-orchestration.md` 零 frontmatter、零 plugin.json 注册、零 README 独立条目，被 5 个 command skill 用指针句消费）；(b) 检查平台原生能力是否已覆盖触发场景（Claude Code 原生就 ship 了 `loop`、`schedule` 等顶层 skill，其 description 已路由 "check my PR every 5 min" 这类 standalone 请求）。

**Why:** 2026-07-08 designing-loops 设计：10 项结构 checklist 全 PASS 后，对抗性评审判 RECONSIDER THE SHAPE——新 auto-loading internal skill 相对 ~5 段真正新内容过度工程。我在 Phase 1 只权衡了"折进 using-superpowers"和"扩展 goal-wrapper.md"两个替代，从没考虑"不加新面"的第三选项；而 simplify-don't-add 先验（[[reference_anthropic_harness_blog]]）当时就在 context 里，没被应用到 shape 决策。失败不是缺信息，是在选形态的时刻没调用已有先验。另外两个结构性事实当时可查而未查：(1) 本 repo 对同类内容的既有处理就是 references 文件；(2) 平台原生 skill 已覆盖 standalone 触发。

**How to apply:**
- 结构 checklist（design-v2）验证的是合规不是比例——PASS ≠ 形态正确。对"新增交付面"类设计，PASS 后加一轮无作者上下文的对抗性 proportionality 评审（明确指令：argue against the shape），成本一个 agent，本次抓到了 generator + 结构评审都没抓到的问题。
- internal skill 的触发精度（description 措辞）在本 repo 无 eval harness 可验证；能删掉触发面就删——不存在的面没有精度问题。
- 别急着把这条教训 ADD 进 brainstorming SKILL.md：单实例证据，按 EVO 纪律（2+ plans）留给 retrospective 聚合；本条 memory 就是聚合输入。
- 关联：[[feedback_skill_level_enforcement]]（注意张力：内容退到 references 文件后没有 L2 CRITICAL 载体——若内容含强制规则，指针句所在的宿主 skill L2 必须承载 CRITICAL；纯 advisory 决策支持内容才适合无面 references 形态）。
