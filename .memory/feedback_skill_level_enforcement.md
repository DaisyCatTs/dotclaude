---
name: feedback_skill_level_enforcement
description: L2 SKILL.md 必须有 CRITICAL 标记；新增 internal skill 的加载指令必须同时落 L2 和 L3
type: feedback
---

任何 agent 必须遵守的规则必须在 L2 SKILL.md body 中有显式 CRITICAL block。仅在 L3 references（`references/*.md`）或目录结构注释中存在的规则会被跳过。

**Why:** 模型只读 L2（SKILL.md body），不自动加载 L3。多次验证确认此失效模式（Workflow opt-in、gate skill 加载指令、bundle 脚本路径都曾只放在 L3 被跳过）。

**How to apply:**
- 向 skill 添加强制约束时，在 SKILL.md（L2）中放 CRITICAL block，不要只放在 references
- 新增 internal skill 时，它的加载指令必须同时落 L2 CRITICAL（body 显式块），哪怕 L3 已写得很细
- 软措辞（`## Pre-operation Checks`、`Note:`、`warn`）会被当成可选建议跳过，升级为显式 CRITICAL
- skill 有多个执行路径时，agent 走第一条匹配——移除竞争路径并重定向到目标路径
- bundle 脚本的可执行指令必须用 `${CLAUDE_PLUGIN_ROOT}/...` 绝对路径，描述性指针（References 节 `- ./scripts/x`）才是裸路径的合法形态