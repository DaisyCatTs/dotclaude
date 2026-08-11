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

ENDPOINT=$(resolve_env "$(echo "$CONFIG" | jq -r '.defaultEndpoint // ""')")
# Endpoint-first with legacy flat-field fallback (matches /pi:delegate). When
# defaultEndpoint is empty, fall back to the flat .provider/.model/.baseUrl/.apiKey.
# Provider stays empty when unset — pi-agent lets pi's own default apply.
PROVIDER=$(resolve_env "$(echo "$CONFIG" | jq -r --arg e "$ENDPOINT" 'if $e != "" then (.endpoints[$e].provider // "") else (.provider // "") end')")
MODEL=$(resolve_env "$(echo "$CONFIG" | jq -r --arg e "$ENDPOINT" 'if $e != "" then (.defaultModel // "") else (.model // "") end')")
BASE_URL=$(resolve_env "$(echo "$CONFIG" | jq -r --arg e "$ENDPOINT" 'if $e != "" then (.endpoints[$e].baseUrl // "") else (.baseUrl // "") end')")
API_KEY=$(resolve_env "$(echo "$CONFIG" | jq -r --arg e "$ENDPOINT" 'if $e != "" then (.endpoints[$e].apiKey // "") else (.apiKey // "") end')")
THINKING=$(resolve_env "$(echo "$CONFIG" | jq -r '.thinking // "max"')")
# Clean mode is default. withPackages:true (or CLI --with-packages) opts into loading
# the user's global pi packages/skills/extensions.
WITH_PACKAGES=$(echo "$CONFIG" | jq -r 'if .withPackages == true then "true" else "" end')
# If model still empty, use the first model from the endpoint.
if [ -z "$MODEL" ] || [ "$MODEL" = "null" ]; then
  MODEL=$(resolve_env "$(echo "$CONFIG" | jq -r --arg e "$ENDPOINT" '.endpoints[$e].models[0] // ""')")
fi

# CLI override: --endpoint / --model re-resolve the active endpoint (highest priority).
# Match only the flag region (after the task description's first -- flag), so a task
# that merely mentions "--endpoint" does not hijack resolution. Accept an endpoint only
# if it exists in .endpoints.
FLAGS_REGION=$(echo "$ARGUMENTS" | awk '{ for(i=1;i<=NF;i++) if($i ~ /^--/) { for(j=i;j<=NF;j++) printf "%s%s", $j, (j<NF?" ":""); break } }')
# Independent blocks so --endpoint and --model combine. When both are given, --endpoint
# is authoritative for the endpoint and --model picks the model; the model scan only
# re-routes the endpoint when no explicit --endpoint was supplied.
if echo "$FLAGS_REGION" | grep -q -- '--endpoint'; then
  CLI_EP=$(echo "$FLAGS_REGION" | sed -n 's/.*--endpoint[= ]\([^ ]*\).*/\1/p' | head -1)
  EP_EXISTS=$(echo "$CONFIG" | jq -r --arg e "$CLI_EP" '.endpoints | has($e)')
  [ "$EP_EXISTS" = "true" ] && ENDPOINT=$(resolve_env "$CLI_EP")
fi
if echo "$FLAGS_REGION" | grep -q -- '--model'; then
  CLI_MODEL=$(echo "$FLAGS_REGION" | sed -n 's/.*--model[= ]\([^ ]*\).*/\1/p' | head -1)
  if [ -n "$CLI_MODEL" ]; then
    EP_MATCH=$(echo "$CONFIG" | jq -r --arg m "$CLI_MODEL" '(.endpoints | to_entries | map(select((.value.models // []) | index($m))) | .[0].key // "")')
    if [ -z "$CLI_EP" ] && [ -n "$EP_MATCH" ]; then
      ENDPOINT=$(resolve_env "$EP_MATCH")
    fi
  fi
fi
# CLI --with-packages: opt into loading global pi packages/skills/extensions.
if echo "$FLAGS_REGION" | grep -q -- '--with-packages'; then
  WITH_PACKAGES="true"
fi
# Re-resolve provider/baseUrl/apiKey for the (possibly CLI-selected) endpoint, and honor
# CLI_MODEL explicitly (a CLI --model must win over any configured defaultModel).
if [ -n "$ENDPOINT" ]; then
  PROVIDER=$(resolve_env "$(echo "$CONFIG" | jq -r --arg e "$ENDPOINT" '.endpoints[$e].provider // ""')")
  if [ -n "$CLI_MODEL" ]; then
    MODEL=$(resolve_env "$CLI_MODEL")
  elif [ -n "$CLI_EP" ]; then
    # CLI --endpoint selected a different endpoint — its defaultModel (if any) belongs
    # to the OLD endpoint, so use the selected endpoint's own first model.
    MODEL=$(resolve_env "$(echo "$CONFIG" | jq -r --arg e "$ENDPOINT" '.endpoints[$e].models[0] // ""')")
  else
    MODEL=$(resolve_env "$(echo "$CONFIG" | jq -r --arg e "$ENDPOINT" '(.defaultModel // .endpoints[$e].models[0] // "")')")
  fi
  BASE_URL=$(resolve_env "$(echo "$CONFIG" | jq -r --arg e "$ENDPOINT" '.endpoints[$e].baseUrl // ""')")
  API_KEY=$(resolve_env "$(echo "$CONFIG" | jq -r --arg e "$ENDPOINT" '.endpoints[$e].apiKey // ""')")
fi
# Model ownership check (AFTER re-resolve, on the final endpoint/model): if the model is
# not in the active endpoint's list (a stale defaultModel from a previous --endpoint switch,
# or a CLI --endpoint whose models don't contain the resolved model), fall back to the
# endpoint's first model so provider and model stay consistent. Skip when a CLI --model
# was given — the user explicitly chose that model (CLI > settings), so do not override it.
if [ -z "$CLI_MODEL" ] && [ -n "$ENDPOINT" ] && [ -n "$MODEL" ] && [ "$MODEL" != "null" ]; then
  IN_ENDPOINT=$(echo "$CONFIG" | jq -r --arg e "$ENDPOINT" --arg m "$MODEL" '(.endpoints[$e].models // []) | index($m) // -1')
  if [ "$IN_ENDPOINT" = "-1" ]; then
    MODEL=$(resolve_env "$(echo "$CONFIG" | jq -r --arg e "$ENDPOINT" '.endpoints[$e].models[0] // ""')")
  fi
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
