# git-agent Plugin (Claude Code)

Claude Code plugin for the [git-agent](https://github.com/FradSer/git-agent) CLI: atomic AI commits, co-change relations, and a PreToolUse guard that blocks raw `git add` / `git commit`.

This tree is only for Claude Code (`@git-agent/` / `/git-agent:*`). It is not packaged for the pi coding harness; that packaging, if any, lives outside this marketplace.

## Prerequisites

- `git-agent` CLI on `PATH`

## Commands

| Command | Purpose |
|---------|---------|
| `/git-agent:commit` | Atomic conventional commits via `git-agent commit` |
| `/git-agent:commit-and-push` | Commit then push |
| `/git-agent:related` | Historical co-change query (`git-agent related`) |
| `/git-agent:init` | Regenerate scopes / `.gitignore` from history |

## Hook

`PreToolUse` on `Bash` runs `hooks/validate-commit-pretool.sh`:

- Denies raw `git commit` and standalone `git add`
- Allows `git add <path> && git-agent commit ...` chains
- Escape hatch: `GIT_SKILL_FALLBACK=1`

## Layout

```
git-agent/
├── .claude-plugin/plugin.json
├── hooks/validate-commit-pretool.sh
├── skills/
│   ├── commit/
│   ├── commit-and-push/
│   ├── related/
│   └── init/
├── references/
└── tests/
```

## License

MIT
