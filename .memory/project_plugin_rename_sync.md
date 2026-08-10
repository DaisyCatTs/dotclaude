---
name: project_plugin_rename_sync
description: 插件改名后 ~/.claude/settings.json 的 enabledPlugins key 不会自动跟随，需手动同步；hooks.json
  外层必须有 hooks 键
type: project
---

dotclaude marketplace 里插件改名（如 superdev → mattpocock）后，`~/.claude/settings.json` 的 `enabledPlugins` 旧 key（`superdev@frad-dotclaude`）不会自动更新，导致 `/plugin` 报 "Plugin not found in marketplace"。改名时需手动把 settings.json 的 enabledPlugins key 改成新名，再 `claude plugin install <newname>@frad-dotclaude`，最后 `claude plugin uninstall <oldname>@frad-dotclaude` 清 orphan。

**Why:** marketplace 与用户级 enabledPlugins 是两个独立状态源，改名只同步 marketplace；旧 key 变孤儿引用。

**How to apply:** 任何插件 rename/remove 后，grep `~/.claude/settings.json` 的 enabledPlugins 和 `~/.claude/plugins/installed_plugins.json`，同步/卸载孤儿。插件级 `hooks/hooks.json` 文件格式必须为 `{ "description": ..., "hooks": { "EventName": [ { "hooks": [{ "type": "command", "command": ... }] } ] } }` —— 顶层直接放事件名（无 `hooks` 外层键）会报 `Invalid input: expected record, received undefined`（vision 插件教训）。官方参考见 `.research/claude-plugins-official/plugins/*/hooks/hooks.json`。

相关：[[project_vision_bridge_plugin]] [[feedback_claude_code_guide]]
