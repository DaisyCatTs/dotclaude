# Docs Index

> docs/ 总索引，一行一文档。手工维护（原 docs-index.sh 已随 superpowers 退役）。

| path | kind | status | summary | updated |
|---|---|---|---|---|
| docs/memory-layer-status.md | reference | active | memory 层约定: docs/memory/ 一文件一事实 + frontmatter 格式 | 2026-08-02 |
| docs/memory/convention_req-trace-explicit-citation.md | memory | active | design-v3 REQ-TRACE-01: explicit (Req #N)/REQ-NNN citations + full-set scan | 2026-07-09 |
| docs/memory/pitfall_bdd-specs-explicit-req-tracing.md | memory | active | bdd-specs.md needs explicit Req# tags per scenario, not just topical naming | 2026-07-07 |
| docs/memory/pitfall_bsd-grep-dash-dash-option.md | memory | active | BSD grep: `-`-prefixed pattern parses as long option; use `--` terminator | 2026-07-31 |
| docs/memory/pitfall_repo-root-claude-project-dir.md | memory | active | repo_root() silently targets parent repo when CLAUDE_PROJECT_DIR unset | 2026-08-01 |
| docs/memory/pitfall_review-package-cd-pwd-corruption.md | memory | active | review-package.sh cd+pwd substitution corrupts PLAN_DIR resolution | 2026-07-06 |
| docs/memory/pitfall_zsh-no-word-split.md | memory | active | zsh does not word-split unquoted $var; iterate via while IFS= read -r | 2026-07-31 |
| docs/orphaned-designs.md | reference | active | 设计索引: orphaned/superseded + active 未实现 (agentbook/designing-loops) | 2026-08-02 |
