---
name: project_gitagent_scopes
description: git-agent scope 管理——init --scope 只看已提交历史；config.yml(14) 与 CLAUDE.md(21)
  已漂移，需手动保持同步
type: project
---

dotclaude 的 commit scope 有**两处**定义,必须保持一致:
- `.git-agent/config.yml` 的 `scopes:`——git-agent 生成 commit message 时**实际读取**的
- `CLAUDE.md` 的 `**Scopes:**` 行——人读文档

2026-08-08 config.yml 已改为缩写风格（hyperframes→hf、marketing→mkt、refactor→ref、office→off、github→gh），但 CLAUDE.md 仍是全名——当前 config.yml 14 个、CLAUDE.md 21 个，已严重漂移。加新插件后必须手动同步两处。

**关键 gotcha:** `git agent init --scope --force` 用 AI 从**已提交的 git 历史**生成 scopes,**不看工作区**。刚创建、还没提交的新插件它扫不到——重新生成只会原样吐回旧列表。

**How to apply:** 加新插件后要 scope,二选一:(a) 先提交插件,再 `git agent init --scope --force`;(b) 直接手动在 config.yml 按现有格式追加 `- name: <scope>` + 描述 `... in <dir>/.`,并同步 CLAUDE.md 的 Scopes 行。命名用混合约定:长名缩写(antigravity→ag、autoresearch→as、hyperframes→hf、marketing→mkt、refactor→ref、plugin-optimizer→po、superpowers→sp、code-context→cctx、hardware→hw、github→gh),短名用全名(git/gitflow/office/swiftui/utils/storm/acpx);memory→mem 已入 config;mattpocock 用 `sd`(原 superdev)只在 CLAUDE.md。**别用 `off` 当 scope**(YAML 把裸 off 解析成布尔 false,得加引号)。参见 [[project_readme_sync_manual]]、[[project_hardware_plugin]]。
