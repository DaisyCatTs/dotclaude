# Delegate Settings Reading

This reference holds the full config-reading snippet for `/pi:delegate`. Load it when the skill needs to resolve provider/model/baseUrl/apiKey from the settings files.

## Reading settings

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
# Base model: resolve defaultModel (or endpoint's first model), used by the ownership
# check below after any CLI override is applied.
# If model still empty, use the first model from the endpoint.
if [ -z "$MODEL" ] || [ "$MODEL" = "null" ]; then
  MODEL=$(resolve_env "$(echo "$CONFIG" | jq -r --arg e "$ENDPOINT" '.endpoints[$e].models[0] // ""')")
fi

# CLI override: --endpoint / --model re-resolve the active endpoint (highest priority).
# Match only the flag region (after the task description's first -- flag), so a task
# that merely mentions "--endpoint" does not hijack resolution. Accept an endpoint only
# if it exists in .endpoints.
FLAGS_REGION=$(echo "$ARGUMENTS" | awk '{ for(i=1;i<=NF;i++) if($i ~ /^--/) { for(j=i;j<=NF;j++) printf "%s%s", $j, (j<NF?" ":""); break } }')
if echo "$FLAGS_REGION" | grep -q -- '--endpoint'; then
  CLI_EP=$(echo "$FLAGS_REGION" | sed -n 's/.*--endpoint[= ]\([^ ]*\).*/\1/p' | head -1)
  EP_EXISTS=$(echo "$CONFIG" | jq -r --arg e "$CLI_EP" '.endpoints | has($e)')
  [ "$EP_EXISTS" = "true" ] && ENDPOINT=$(resolve_env "$CLI_EP")
elif echo "$FLAGS_REGION" | grep -q -- '--model'; then
  CLI_MODEL=$(echo "$FLAGS_REGION" | sed -n 's/.*--model[= ]\([^ ]*\).*/\1/p' | head -1)
  if [ -n "$CLI_MODEL" ]; then
    EP_MATCH=$(echo "$CONFIG" | jq -r --arg m "$CLI_MODEL" '(.endpoints | to_entries | map(select((.value.models // []) | index($m))) | .[0].key // "")')
    [ -n "$EP_MATCH" ] && ENDPOINT=$(resolve_env "$EP_MATCH")
  fi
fi
# CLI --api-key: a key the user typed explicitly overrides the config-file key.
# It is already in the user's prompt, so passing it to pi-agent is not a config-secret leak.
if echo "$FLAGS_REGION" | grep -q -- '--api-key'; then
  CLI_API_KEY=$(echo "$FLAGS_REGION" | sed -n 's/.*--api-key[= ]\([^ ]*\).*/\1/p' | head -1)
  [ -n "$CLI_API_KEY" ] && API_KEY=$(resolve_env "$CLI_API_KEY")
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
  # CLI --api-key wins: only re-resolve API_KEY from config when the user did not type one.
  [ -z "$CLI_API_KEY" ] && API_KEY=$(resolve_env "$(echo "$CONFIG" | jq -r --arg e "$ENDPOINT" '.endpoints[$e].apiKey // ""')")
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

The `$VAR` references inside JSON values are resolved at read time by `resolve_env`. (pi reads its own provider env vars — `OPENAI_API_KEY`, etc. — as its last-resort default, so you do not need to set them when a config file or flag provides the key.)
