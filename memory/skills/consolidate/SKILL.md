---
name: consolidate
description: Consolidates and normalizes the project's memory across .memory/ (canonical, git-tracked) and ~/.claude/projects/.../memory/ (harness). Also covers active writing — when you encounter something worth remembering, write it immediately.
user-invocable: true
allowed-tools: ["Read", "Write", "Glob", "Grep"]
---

# Memory — Active Write & Consolidate

The project's memory lives in two locations that must stay **identical** (idempotent):

1. **`~/.claude/projects/<escaped-cwd>/memory/`** — harness, loaded by Claude Code, written first
2. **`.memory/`** — canonical, git-tracked, written second

Resolve the harness path: `~/.claude/projects/<cwd-with-/→->/memory/` (probe both space-handling forms: `/→-`+` →-` and `/→-`+space-kept).

## Active Write

When you encounter a decision, preference, lesson, or anything worth remembering, write it **immediately** during the conversation — do not wait for /memory:consolidate.

### Privacy check

`.memory/` is part of a **public GitHub repo**. Before writing to `.memory/`, check for:
- API keys, tokens, secrets, passwords
- Personal identifiable information (email, account IDs)
- Credentials, private URLs, access keys
- **User preferences, behavioral patterns, personal workflow habits** — anything that identifies how the user works personally
- Any information that would be a security or privacy risk if published

Safe (pure technical/development content) → write to both locations. Contains private data → write to harness only, MEMORY.md index note `(harness only)`.

### How to write

1. Write file to `~/.claude/projects/.../memory/<filename>.md` (harness, session-visible)
2. Write **identical** file to `.memory/<filename>.md` (canonical, git-tracked) — skip if private
3. Update `MEMORY.md` in both locations with same index line

File naming: `<type>_<kebab-slug>.md` (type: feedback, project, reference)

Format:
```markdown
---
name: <kebab-slug>
description: <one-line hook>
type: feedback | project | reference
---

<the fact>

**Why:** <why this decision exists>

**How to apply:** <actionable rules>

**Related:** [[other-memory]] [[another-memory]]
```

## CRITICAL: Memory is decision log, not operation log

Every memory file answers two questions only:
- **Why** — why this decision or rule exists
- **How to apply** — what to do next time

Remove all operation history (version numbers, dates-as-timeline, "first X then Y"). That lives in `git log`. Keep only the durable rationale and actionable rules.

## CRITICAL: MEMORY.md index format

Each line: one concise sentence, no version numbers, no date ranges, no timeline descriptions.

Good: `feedback_git_commit_hook_needed.md — git PreToolUse hook intercepts git add/commit, redirects to /git:commit; allows chain + GIT_SKILL_FALLBACK=1 escape`
Bad:  `feedback_git_commit_hook_needed.md — git PreToolUse hook intercepts git add/commit; v0.5.3 command position anchoring + two exceptions + 26 regression tests`

## Red lines

- Never drop `[[name]]` cross-links when rewriting — preserve all from the original
- Never delete a file referenced by `[[name]]` in another memory file unless the reference is also removed

## Consolidate (/memory:consolidate)

User-invoked only. Consolidate in harness memory first, then sync to `.memory/`.

### 1. Read every file

Read every `*.md` in both harness memory and `.memory/`, including `MEMORY.md`. Detect drift.

### 2. Normalize

- Relative dates → absolute `YYYY-MM-DD`
- Frontmatter: `name`, `description`, `type` only (no `node_type`, `originSessionId`, `modified`)
- `description` must be specific enough to distinguish from similar files

### 3. Deduplicate and merge

Merge duplicates; keep the most detailed.

### 4. Prune

Keep active-project facts and highly-`[[linked]]` ones. Prune:
- Dormant (6+ months, no durable lesson)
- Expired time-bound notes (keep transferable insights)
- Operational snapshots older than 3 months (date-mark survivors)
- Operation history: version numbers, step-by-step timelines

### 5. Rewrite for concision

- **Why** — root cause or decision rationale (1-3 paragraphs max)
- **How to apply** — actionable rules (bullet list preferred)
- **Related** — `[[name]]` cross-links

### 6. Rebuild index

If anything changed, rewrite `MEMORY.md` — one line per file, under 50 lines, no version/date.

### 7. Sync to `.memory/`

For each file in harness memory:
1. If **safe** (public/technical, no user preferences) → copy to `.memory/`
2. If **private** (credentials, personal info, user preferences) → skip, leave in harness only
3. Delete `*.md` in `.memory/` that are not in harness memory (safe files only)

## Report

Files read, files changed (path + one-line reason), facts merged/pruned/skipped, index rebuilt yes/no. If nothing changed, say so.