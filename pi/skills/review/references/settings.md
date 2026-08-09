# pi Settings Reference

This reference is loaded by `SKILL.md` when `/pi:review` needs the full settings format, reading logic, `--edit-config`, or `--list-models` behavior. The main file links here.

## Resolution chain (highest priority first)

1. **CLI flag** (from `$ARGUMENTS`)
2. **`.claude/pi.local.json`** — project-specific overrides, gitignored
3. **`.claude/pi.json`** — project shared defaults, committed
4. **`~/.claude/pi.local.json`** — global user-wide defaults
5. **Built-in defaults** (listed in SKILL.md)

## Settings file format

The settings file maps **named endpoint configurations** (user-defined keys) to pi's known providers. Each key can have its own `baseUrl`, `apiKey`, and `models` list. At runtime, the skill writes the chosen endpoint's `baseUrl` into `~/.pi/agent/models.json` under a known provider (default `openai`), then calls pi with `--provider openai`.

Values can reference environment variables using `$VAR` or `${VAR}` syntax — they are resolved at read time. This is useful for API keys: `"apiKey": "$MY_API_KEY"` reads from the environment variable at runtime.

All fields are optional. The example below shows the format — fill in your own endpoints:

```json
{
  "endpoints": {
    "my-proxy": {
      "provider": "openai",
      "baseUrl": "http://10.10.0.195:8317/v1",
      "models": ["gemini-3.6-flash-high", "gemini-3.6-pro"]
    }
  },
  "defaultEndpoint": "my-proxy",
  "defaultModel": "gemini-3.6-flash-high"
}
```

Each endpoint entry has:
- `provider` (required) — pi's known provider name (`openai`, `anthropic`, `google`, etc.). This is what pi's `--provider` flag receives.
- `baseUrl` (optional) — custom API endpoint. When present, the pi-agent writes it to the agent-dir `models.json` (default `~/.pi/agent/models.json`, redirectable via `PI_CODING_AGENT_DIR`/`AGENT_DIR`) for the specified `provider` before running.
- `apiKey` (optional) — API key or `$ENV_VAR` reference, passed to pi via `--api-key`.
- `models` — array of model IDs available via this endpoint.

Only include fields the user wants to override. Partial files are fine — the chain merges per-field.

## Reading settings

Before parsing `$ARGUMENTS`, read the settings files in priority order (lowest first, so each overrides the previous):

```bash
# Start with empty config
CONFIG='{}'

# 1. Global personal (lowest priority)
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

Then extract values, resolving environment variable references:

```bash
# Resolve env vars in a JSON value: "$VAR" or "${VAR}" → actual value
resolve_env() {
  local val="$1"
  while [[ "$val" =~ \$\{?([a-zA-Z_][a-zA-Z0-9_]*)\}? ]]; do
    local var_name="${BASH_REMATCH[1]}"
    local var_value="${!var_name:-}"
    val="${val//${BASH_REMATCH[0]}/$var_value}"
  done
  echo "$val"
}

ENDPOINT=$(resolve_env "$(echo "$CONFIG" | jq -r '.defaultEndpoint // ""')")
# Endpoint-first with legacy flat-field fallback (matches /pi:delegate). When
# defaultEndpoint is empty, fall back to the flat .provider/.model/.baseUrl/.apiKey.
# Provider stays empty when unset — pi-agent lets pi's own default apply.
PROVIDER=$(resolve_env "$(echo "$CONFIG" | jq -r --arg e "$ENDPOINT" 'if $e != "" then (.endpoints[$e].provider // "") else (.provider // "") end')")
MODEL=$(resolve_env "$(echo "$CONFIG" | jq -r --arg e "$ENDPOINT" 'if $e != "" then (.defaultModel // "") else (.model // "") end')")
BASE_URL=$(resolve_env "$(echo "$CONFIG" | jq -r --arg e "$ENDPOINT" 'if $e != "" then (.endpoints[$e].baseUrl // "") else (.baseUrl // "") end')")
API_KEY=$(resolve_env "$(echo "$CONFIG" | jq -r --arg e "$ENDPOINT" 'if $e != "" then (.endpoints[$e].apiKey // "") else (.apiKey // "") end')")
THINKING=$(resolve_env "$(echo "$CONFIG" | jq -r '.thinking // "max"')")
# If model still empty, use the first model from the endpoint (handles defaultModel: "")
if [ -z "$MODEL" ] || [ "$MODEL" = "null" ]; then
  MODEL=$(resolve_env "$(echo "$CONFIG" | jq -r --arg e "$ENDPOINT" '.endpoints[$e].models[0] // ""')")
fi
```

## `--edit-config` flag

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
  CONFIG_PATH=".claude/pi.local.json"
fi

# Create if not exists
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

Report: "Settings file created/opened at `<path>`. Changes take effect on the next `/pi:review` invocation."

## `--list-models` flag

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

Then stop — do not proceed to review.
