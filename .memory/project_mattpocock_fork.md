---
name: project_mattpocock_fork
description: mattpocock 插件 = mattpocock/skills 全量 fork + BDD(替代tdd) + 自改进子系统；与 superpowers
  并存
type: project
---

fork 自 [mattpocock/skills](https://github.com/mattpocock/skills)，当前基线 **v1.2.3**，注册 **27 skill**。插件名 `mattpocock`，skill 前缀 `/mattpocock:`。

## 关键改造

1. **TDD 流程改 BDD**：上游 tdd 改名为 bdd，内容换 superpowers 的 BDD（Gherkin/.feature/Iron Law/discovery→formulation→automation，保留 mattpocock 的 seams/vertical-slice/tracer-bullet）。`/implement` 驱动 `/bdd`；`to-spec` 产 Gherkin 场景；`code-review` 的 spec 轴对 Gherkin 场景核验。
2. **tdd 为 BDD-driven TDD（BDD Automation 阶段）**：非独立实践，不可加 `disable-model-invocation`（bdd/implement 需要能加载它），用 SKILL.md 顶部 CRITICAL 检查替代技术门控。直接调用时先问用户 Gherkin 场景是否已定义，否则 redirect 到 bdd。
3. **移植自改进子系统（重实现）**：retrospective + checklists（design→spec、plan→tickets、code 保留）+ evolution-log + memory pitfalls；evaluator 折进 `/code-review` 的 Standards+Spec sub-agents。lib 只留 `jsonl-emit` + `seed-checklists`。

## 同步规则

- 不能整目录覆盖——上游同步永远**先拉上游 → diff → 选择性修改**（因本地有大量 frontmatter/CRITICAL/AskUserQuestion 改写）
- 同步时做"上游有而本地没有"的完整性扫描（`diff -rq` + `find` 缺失清单），不能只 diff 增量
- 移动 skill 到不同 invocation 形态的 bucket 时，必须检查并清除 frontmatter 的 `disable-model-invocation` flag
- 版本同步点：plugin.json + marketplace.json + README.md + 顶层双语 README，四处一致
- 同步流程固化在 `mattpocock/SYNC.md`，每次同步前先读

## 交叉引用规则

- 注册 skill 必须在 `ask-matt/SKILL.md` 的 Standalone 或主流程中提及
- 每处 `/mattpocock:` 引用必须指向已注册且存在的 skill 目录
- tdd 的 CRITICAL 检查在文件顶部，不依赖 `disable-model-invocation`
- 多文件核心变更后跑独立审计 agent（fresh-agent audit rule）

## 关联

[[project_superpowers_hooks]] [[project_active_design_work]] [[project_readme_sync_manual]] [[feedback_skill_level_enforcement]] [[feedback_self_audit_caught_my_bugs]]