---
name: project_readme_sync_manual
description: 顶层双语 README 必须手动同步——/utils:update-readme 禁用了模型调用
type: project
---

`utils/skills/update-readme/SKILL.md` 设了 `disable-model-invocation: true`,所以 Claude 无法用 Skill 工具调用 `/utils:update-readme`(会报 "Unknown skill");它只能由用户手动输入 `/utils:update-readme` 触发。

**Why:** 该 skill 被设计为仅用户手动触发,避免模型自动改写 README。CLAUDE.md 只说"增删插件后跑 /utils:update-readme",没提模型其实调不动它。

**How to apply:** 新增/删除/重命名插件后,自己手动同步 `README.md` 和 `README.zh-CN.md` 三处:(1) 顶部徽章 `plugins-N`;(2) 简介句里的插件数量;(3) 在 storm 条目之后插入新插件块(`### [name](name/)` 标题 + 一句话描述 + `**Installation:**` 安装命令 + `---`)。中文版用自然简体中文、避免「赋能/助力/生态」类 AI 腔。注意原有计数可能已过时(2026-06 这次发现徽章停在 13、文案停在 15,实际 15),顺手修正到真实数量。同时记得 `marketplace.json` 顶部 version 做 minor bump。参见 [[project_active_design_work]]。
