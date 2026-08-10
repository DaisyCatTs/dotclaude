# Memory Plugin

Active memory writing during conversation, plus manual `/memory:consolidate` for tidying up. No auto-consolidation.

Two locations must stay **identical** (idempotent):

1. **`~/.claude/projects/<escaped-cwd>/memory/`** — harness, loaded by Claude Code, written first
2. **`.memory/`** — canonical, git-tracked, written second

**Privacy:** `.memory/` is part of a public GitHub repo. Technical content only; user preferences, credentials, and personal information stay in harness memory only.

**Version**: 0.1.3

## Installation

```bash
claude plugin install memory@frad-dotclaude
```

## How it works

- **Active writing**: when the model encounters a decision, preference, or lesson worth remembering, it writes to harness memory then mirrors to `.memory/` immediately — no hook needed.
- **Slash command** `/memory:consolidate` — user-invoked only. Normalizes, deduplicates, prunes, and rebuilds the index in harness, then syncs safe files to `.memory/`.

## Files

```
memory/
├── .claude-plugin/plugin.json   # commands only (no hooks)
├── skills/consolidate/SKILL.md  # all memory logic (active write + consolidate instructions)
└── README.md
.memory/                         # canonical git-tracked memory data
```