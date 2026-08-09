---
name: delegate
description: Delegates a coding task to pi (dev/pi), a minimal terminal coding harness. This skill should be used when the user asks to "use pi", "run pi", "delegate to pi", "let pi handle this", "ask pi to", "have pi do", or invokes /pi:delegate. It bridges the current Claude Code context to the pi CLI, passing relevant files, git state, and the task description for execution by the pi-agent.
user-invocable: true
argument-hint: "<task description> [--endpoint ENDPOINT] [--provider PROVIDER] [--model MODEL] [--api-key KEY] [--thinking LEVEL] [--tools TOOL_LIST] [--exclude-tools TOOL_LIST] [--no-git] | --edit-config [--local|--shared|--global] | --list-models | --doctor"
allowed-tools: ["Task", "Bash(git:*)", "Bash(jq:*)", "Bash(ls:*)", "Bash(find:*)", "Bash(cat:*)", "Bash(mkdir:*)", "Bash(mv:*)", "Bash(echo:*)", "Bash(command:*)", "Bash(grep:*)", "Bash(head:*)", "Bash(vi:*)", "Read", "Grep", "Glob"]
---

# CRITICAL: pi CLI Integration

This skill delegates a task to the `pi` CLI tool (`@earendil-works/pi-coding-agent`) via the dedicated `pi:pi-agent` execution layer. Config is read endpoint-first (same format as `/pi:review`); legacy flat fields remain as a fallback.

## Before Execution: Check Installation

```bash
# Check if pi is installed
command -v pi >/dev/null 2>&1
```

If not installed, tell the user:
```
pi is not installed. Install it globally:

  npm install -g @earendil-works/pi-coding-agent

Or via the standalone installer:

  curl -fsSL https://pi.dev/install.sh | sh
```

Then stop — do not proceed without pi installed.

## Persistent Settings

User preferences persist across invocations via JSON files. The resolution chain (highest priority first):

1. **CLI flag** (from `$ARGUMENTS`)
2. **`.claude/pi.local.json`** — project-specific overrides, gitignored
3. **`.claude/pi.json`** — project shared defaults, committed
4. **`~/.claude/pi.local.json`** — global user-wide defaults
5. **pi's own defaults** (pi decides its own default provider and model)

Provider/model/baseUrl/apiKey come from these files (or CLI flags). API keys reach pi via `--api-key` — nothing is written to `models.json` except `baseUrl`. pi itself reads the usual provider env vars (`OPENAI_API_KEY`, etc.) as its own last-resort defaults.

### Settings file format

The settings file uses the **same named-endpoint format as `/pi:review`** — endpoint-first. Legacy flat fields (`provider`, `model`, `baseUrl`, `apiKey`) are still honored as a fallback when no `defaultEndpoint` is set, so existing configs keep working.

Values can reference environment variables using `$VAR` or `${VAR}` syntax — they are resolved at read time.

```json
{
  "endpoints": {
    "local-proxy": {
      "provider": "openai",
      "baseUrl": "http://10.10.0.195:8317/v1",
      "models": ["gemini-3.6-flash-high", "gemini-3.6-pro"]
    }
  },
  "defaultEndpoint": "local-proxy",
  "defaultModel": "gemini-3.6-flash-high"
}
```

Each endpoint key has `provider` (required), optional `baseUrl`, optional `apiKey`, and `models` (array). Only include fields you want to override — partial files merge per-field across the chain.

**Note on precedence:** endpoint-first resolution means that once a `defaultEndpoint` exists anywhere in the merged chain, the active endpoint wins and a project's legacy flat fields (`provider`/`model`/`baseUrl`) are ignored for that key. If you need a project to override the global endpoint, set that project's `.claude/pi.local.json` `defaultEndpoint` to its own endpoint — the flat fields are only consulted when no `defaultEndpoint` is set at all.

### Reading settings

Read the settings files in priority order (lowest first, so each overrides the previous):

```bash
# Start with empty config
CONFIG='{}'

# 1. Global personal (lowest file priority)
if [ -f "$HOME/.claude/pi.local.json" ]; then
  CONFIG=$(jq -s '.[0] * .[1]' /dev/stdin "$HOME/.claude/pi.local.json" 2>/dev/null <<<"$CONFIG" || echo "$CONFIG")
fi

# 2. Project shared
if [ -f ".claude/pi.json" ]; then
  CONFIG=$(jq -s '.[0] * .[1]' /dev/stdin ".claude/pi.json" 2>/dev/null <<<"$CONFIG" || echo "$CONFIG")
fi

# 3. Project personal (highest file priority)
if [ -f ".claude/pi.local.json" ]; then
  CONFIG=$(jq -s '.[0] * .[1]' /dev/stdin ".claude/pi.local.json" 2>/dev/null <<<"$CONFIG" || echo "$CONFIG")
fi
```

Then extract values, resolving environment variable references. Endpoint-first with flat-field fallback:

```bash
# Resolve env vars in a JSON value: "$VAR" or "${VAR}" → actual value.
# NOTE: requires bash — the `BASH_REMATCH` capture is bash-only; under zsh this
# returns the literal `$VAR`. Run the config-reading snippet under bash.
resolve_env() {
  local val="$1"
  while [[ "$val" =~ \$\{?([a-zA-Z_][a-zA-Z0-9_]*)\}? ]]; do
    local var_name="${BASH_REMATCH[1]}"
    local var_value="${!var_name:-}"
    val="${val//${BASH_REMATCH[0]}/$var_value}"
  done
  echo "$val"
}

# Endpoint-first; legacy flat fields fill in when no defaultEndpoint is set
ENDPOINT=$(resolve_env "$(echo "$CONFIG" | jq -r '.defaultEndpoint // ""')")
# Provider stays empty when unset — pi-agent lets pi's own default apply.
PROVIDER=$(resolve_env "$(echo "$CONFIG" | jq -r --arg e "$ENDPOINT" 'if $e != "" then (.endpoints[$e].provider // "") else (.provider // "") end')")
MODEL=$(resolve_env "$(echo "$CONFIG" | jq -r --arg e "$ENDPOINT" 'if $e != "" then (.defaultModel // "") else (.model // "") end')")
BASE_URL=$(resolve_env "$(echo "$CONFIG" | jq -r --arg e "$ENDPOINT" 'if $e != "" then (.endpoints[$e].baseUrl // "") else (.baseUrl // "") end')")
API_KEY=$(resolve_env "$(echo "$CONFIG" | jq -r --arg e "$ENDPOINT" 'if $e != "" then (.endpoints[$e].apiKey // "") else (.apiKey // "") end')")
THINKING=$(resolve_env "$(echo "$CONFIG" | jq -r '.thinking // "max"')")
TOOLS=$(resolve_env "$(echo "$CONFIG" | jq -r '.tools // ""')")
EXCLUDE_TOOLS=$(resolve_env "$(echo "$CONFIG" | jq -r '.excludeTools // ""')")
# If model still empty, use the first model from the endpoint (handles defaultModel: "")
if [ -z "$MODEL" ] || [ "$MODEL" = "null" ]; then
  MODEL=$(resolve_env "$(echo "$CONFIG" | jq -r --arg e "$ENDPOINT" '.endpoints[$e].models[0] // ""')")
fi
```

The `$VAR` references inside JSON values are resolved at read time by `resolve_env`. (pi reads its own provider env vars — `OPENAI_API_KEY`, etc. — as its last-resort default, so you do not need to set them when a config file or flag provides the key.)

### `--edit-config` flag

When `$ARGUMENTS` is exactly `--edit-config` (with optional scope flag), open the settings file for editing. Three scopes matching the three priority tiers:

| Scope | Flag | Path | Description | Git |
|-------|------|------|-------------|-----|
| Project personal | `--edit-config` (default) or `--edit-config --local` | `.claude/pi.local.json` | Per-project overrides | gitignored |
| Project shared | `--edit-config --shared` | `.claude/pi.json` | Team defaults, committed | tracked |
| Global personal | `--edit-config --global` or `--edit-config -g` | `~/.claude/pi.local.json` | User-wide across all projects | user home |

**Shared scope (`--shared`) is committed to git** — never put a literal `apiKey` in it. The `apiKey` field there must be a `$ENV_VAR` reference (e.g. `"$MY_API_KEY"`) so no secret is committed. Literal keys belong in the personal scopes (`.claude/pi.local.json`, `~/.claude/pi.local.json`).

```bash
# Detect scope
if [[ "$ARGUMENTS" == *"--global"* || "$ARGUMENTS" == *"-g"* ]]; then
  CONFIG_PATH="$HOME/.claude/pi.local.json"
elif [[ "$ARGUMENTS" == *"--shared"* ]]; then
  CONFIG_PATH=".claude/pi.json"
else
  # --local (default)
  CONFIG_PATH=".claude/pi.local.json"
fi

# Create if not exists (seed matches the review skill's template)
mkdir -p "${CONFIG_PATH%/*}"
if [ ! -f "$CONFIG_PATH" ]; then
  cat > "$CONFIG_PATH" << 'EOF'
{
  "endpoints": {},
  "defaultEndpoint": "",
  "defaultModel": "",
  "thinking": ""
}
EOF
fi

# Open in editor
${EDITOR:-vi} "$CONFIG_PATH"
```

Report: "Settings file created/opened at `<path>`. Changes take effect on the next `/pi:delegate` invocation."

### `--list-models` flag

When `$ARGUMENTS` is exactly `--list-models`, read the merged config and display all configured endpoints and their models:

```bash
# Endpoints present → list them; otherwise fall back to flat fields
if echo "$CONFIG" | jq -e '.endpoints | length > 0' >/dev/null 2>&1; then
  echo "$CONFIG" | jq -r '
    .defaultEndpoint as $def |
    .defaultModel as $defm |
    ((.endpoints // {}) | to_entries[] |
      "\(.key)" + if .key == $def then " (default)" else "" end +
      " → " + .value.provider +
      ":" +
      ((.value.models // []) | join(", ")) +
      if .key == $def and $defm != "" then "  ← active: " + $defm else "" end
    )
  '
else
  echo "$CONFIG" | jq -r '"flat: " + (.provider // "") + " / " + (.model // "") + " @ " + (.baseUrl // "(default)")'
fi
```

Then stop — do not proceed to delegate.

### `--doctor` flag

When `$ARGUMENTS` is exactly `--doctor`, run a comprehensive configuration check. First run the "Reading settings" snippet above so `$PROVIDER`/`$MODEL`/`$BASE_URL`/`$API_KEY` are populated — the doctor script prints them, and running it before reading settings would wrongly report "pi default"/"not set". Then run the script in `references/doctor.md`.

## Argument Parsing

Parse `$ARGUMENTS` to extract the task description and optional flags. The task description is everything before the first `--` flag. If no flags are present, the entire argument is the task description.

| Flag | Description | Source Priority |
|------|-------------|-----------------|
| `--endpoint` | Endpoint key name (must match a key in settings `endpoints`) | CLI > settings > `defaultEndpoint` |
| `--provider` | LLM provider (anthropic, openai, google, etc.) | CLI > settings > endpoint/provider > pi's default |
| `--model` | Model pattern or ID (e.g. `claude-sonnet-4-20250514`, `openai/gpt-4o`) | CLI > settings > endpoint models > pi's default |
| `--api-key` | API key for the provider | CLI > settings > env var or config file |
| `--thinking` | Thinking level (off/minimal/low/medium/high/xhigh/max) | CLI > settings > `max` |
| `--tools` | Comma-separated allowed tools list | CLI > settings > `read,bash,write,edit,grep,find,ls` |
| `--exclude-tools` | Comma-separated blocked tools list | CLI > settings > (none) |
| `--no-git` | Skip collecting git context | CLI > settings > `false` |

### Resolution order per flag

For each flag, resolve the value by checking CLI flag first, then settings file, then pi's built-in default:

1. Parse `$ARGUMENTS` for that flag. If present, use it.
2. Otherwise, read from `$CONFIG` (the merged settings). If non-null/non-empty, use it.
3. Otherwise, use pi's built-in default.

### Endpoint resolution

1. If `--endpoint` is specified, use it as the key into `endpoints` config.
2. If `--model` is specified without `--endpoint`, scan all endpoints for a model matching the ID — use the first match's endpoint.
3. Otherwise, use `defaultEndpoint` from settings.
4. Resolve the pi provider from the endpoint's `provider` field; the model from `defaultModel` then the endpoint's first `models` entry.
5. If no endpoint is configured, fall back to legacy flat fields (`provider`/`model`/`baseUrl`).

## Delegating to pi-agent

Do NOT run `pi` directly. After parsing arguments and resolving settings, launch the dedicated `pi:pi-agent` execution layer with the Task tool. It builds the command, runs pi in the background, and verifies the outcome.

**Pass these fields in the agent prompt:**

```
MODE: delegate
TASK: <task description>
PROVIDER: <resolved or empty — leave pi's default>
MODEL: <resolved or empty — leave pi's default>
API_KEY: <resolved or empty>
BASE_URL: <resolved or empty — pi-agent writes it to the agent-dir models.json>
AGENT_DIR: <optional — pi agent dir; default ~/.pi/agent. Set to a worktree-local path (e.g. .pi-agent) in sandboxed/git-worktree sessions so pi state stays inside the project>
THINKING: <resolved, default max>
TOOLS: <resolved, default read,bash,write,edit,grep,find,ls>
EXCLUDE_TOOLS: <resolved from --exclude-tools or empty>
NO_GIT: <true if --no-git>
APPEND_PATHS: <(omit — the pi-agent adds CLAUDE.md itself, and collects git context per NO_GIT)>
```

The pi-agent handles: agent-dir resolution, CLAUDE.md context, git context (unless `--no-git`), command construction, background execution (no timeout), and verification via `git diff --stat`.

### Worktree / sandboxed sessions

In a git-worktree or sandboxed session, `$HOME/.pi` is outside the worktree and writes to it get rejected. Two mitigations, applied by the pi-agent:
- `AGENT_DIR` — pass a worktree-local directory (e.g. `.pi-agent`); pi keeps all its state there via `PI_CODING_AGENT_DIR`. Best for isolated sessions.
- Conditional write — once a `BASE_URL` already matches the agent-dir `models.json`, the pi-agent skips the write entirely, so an already-configured endpoint causes no out-of-worktree write.

### `--base-url` note

pi does not support a `--base-url` CLI flag. Custom endpoints are configured through the agent-dir `models.json`, which the pi-agent writes when `BASE_URL` is non-empty — never pass `--base-url` to pi.

## Handling Output

### CRITICAL: pi's Real Output Is File Edits, Not stdout

**pi writes code by editing files in the working directory. Its stdout is secondary — often empty or minimal, especially with long `--append-system-prompt`.** Do not judge success by stdout content.

| Signal | Meaning |
|--------|---------|
| Exit code 0 | pi completed successfully |
| Exit code 1 | pi failed (check stderr) |
| stdout empty | Normal — pi already applied edits to files |
| Modified files exist | Reliable indicator of work done |

### On Success (exit code 0)

The pi-agent reports the changed files. Present those changes to the user and describe what pi modified (additions, deletions, file count). If git shows no changes and exit was 0, the task was understood but resulted in no modifications (read-only analysis, conceptual questions, or the task was already satisfied).

### On Error (exit code 1+)

Show the error message from the pi-agent's report. Common error causes:
- pi not configured (no API key)
- Provider/model not available
- Task interrupted or killed

## Usage Examples

### Basic task with file context
User: `/pi:delegate review the TypeScript types in src/`

Claude: Reads settings, resolves the endpoint, then launches `pi:pi-agent` with `MODE: delegate` and the task description. pi-agent builds the pi command, runs it in the background, and reports `git diff --stat`.

### Specific model
User: `/pi:delegate refactor this component --model claude-sonnet-4-20250514`

Claude: Resolves `--model` from the flag (overriding settings), then passes `MODEL: claude-sonnet-4-20250514` to pi-agent.

### Custom base URL (OpenAI-compatible proxy)
User: `/pi:delegate write unit tests for this module --endpoint local-proxy`

Claude: Resolves the `local-proxy` endpoint from settings, extracts its `baseUrl`, and passes it to pi-agent, which writes it to the agent-dir `models.json` (default `~/.pi/agent/models.json`) before running pi.

### Read-only analysis
User: `/pi:delegate audit the security of this codebase --tools read,grep,find,ls`

Claude: Passes `TOOLS: read,grep,find,ls` to pi-agent so pi is restricted to read-only tools.

### No git context, just conceptual
User: `/pi:delegate explain how React reconciliation works --no-git`

Claude: Passes `NO_GIT: true` along with the task description to pi-agent, so it skips collecting git status/log context.

## Important Notes

- pi MUST be installed globally. The skill checks and blocks if not found.
- **Never run pi directly — always delegate to `pi:pi-agent`.** The agent is the plugin's single execution path and owns backgrounding, verification, and error handling.
- Settings are shared with `/pi:review` via the same file chain (`.claude/pi.local.json`, `.claude/pi.json`, `~/.claude/pi.local.json`) and the same endpoint-first format.
- `--no-session` prevents pi from creating session files; `--no-context-files` prevents pi from reading its own AGENTS.md/CLAUDE.md (which could conflict with the current project's context); `--approve` skips any project trust prompts. The pi-agent adds these.
- **CLAUDE.md context is always passed** by pi-agent via `--append-system-prompt` as file paths — `~/.claude/CLAUDE.md` (user global) and `./CLAUDE.md` (project).
- To configure pi (provider, model, base URL), run `/pi:setup` instead of passing flags manually.
