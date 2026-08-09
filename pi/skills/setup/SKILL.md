---
name: setup
description: Guides the user through configuring pi — provider, model, base URL, and API key. Use when the user asks to "setup pi", "configure pi", "pi setup", "set up pi provider", "pi config", "change pi model", or invokes /pi:setup. Only run this skill when the user explicitly requests pi setup — never auto-invoke.
user-invocable: true
argument-hint: "[--endpoint NAME] [--provider PROVIDER] [--model MODEL] [--base-url URL] [--api-key KEY] | --edit-config | --list-models | --test | --doctor"
allowed-tools: ["Bash(pi:*)", "Bash(jq:*)", "Bash(cat:*)", "Bash(mkdir:*)", "Bash(mv:*)", "Bash(echo:*)", "Bash(command:*)", "Bash(ls:*)", "Bash(vi:*)", "Read", "Write"]
---

# CRITICAL: User setup only — do not auto-invoke

This skill is for **human-only** setup. Never invoke it automatically. Only run when the user explicitly calls `/pi:setup`. Configure pi's provider, model, and endpoint so `/pi:delegate` and `/pi:review` can use them without repeating flags.

## Before Execution: Check Installation

```bash
command -v pi >/dev/null 2>&1
```

If not installed, guide the user:

```bash
npm install -g @earendil-works/pi-coding-agent
```

Or via the standalone installer:

```bash
curl -fsSL https://pi.dev/install.sh | sh
```

Then stop — do not proceed without pi installed.

## Settings File

Both `/pi:delegate` and `/pi:review` read from the same settings chain:

1. **CLI flag** (from `$ARGUMENTS`)
2. **`.claude/pi.local.json`** — project-specific overrides, gitignored
3. **`.claude/pi.json`** — project shared defaults, committed
4. **`~/.claude/pi.local.json`** — global user-wide defaults
5. **pi's own defaults** (pi decides its own default provider and model)

This skill writes to `~/.claude/pi.local.json` (global, takes effect for all projects).

### Settings file format

The settings file uses the **named-endpoint format** shared by `/pi:delegate` and `/pi:review`. All fields are optional — only override what you want to change.

Values can reference environment variables using `$VAR` or `${VAR}` syntax — they are resolved at read time by `/pi:delegate` and `/pi:review`. This is useful for API keys: `"apiKey": "$MY_API_KEY"` reads from the environment variable at runtime.

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
  "defaultModel": "gemini-3.6-flash-high",
  "thinking": "max"
}
```

Each endpoint key has:
- `provider` (required) — pi's known provider name (`openai`, `anthropic`, `google`, etc.)
- `baseUrl` (optional) — custom API endpoint; when present it is written to `~/.pi/agent/models.json` at runtime
- `apiKey` (optional) — API key or `$ENV_VAR` reference
- `models` — array of model IDs available via this endpoint

Legacy flat fields (`provider`/`model`/`baseUrl`/`apiKey`) are still honored by the delegate skill as a fallback when no `defaultEndpoint` is set, but new setups should use the endpoint format.

### `--list-models` flag

When `$ARGUMENTS` is exactly `--list-models`, read the current settings and show the effective configuration:

```bash
echo "=== Current pi configuration ==="
echo "Settings file: $HOME/.claude/pi.local.json"
if [ -f "$HOME/.claude/pi.local.json" ]; then
  cat "$HOME/.claude/pi.local.json"
else
  echo "(not configured — pi uses its defaults)"
fi
echo ""
echo "To configure, run: /pi:setup --endpoint <name> --provider <name> --model <id> [--base-url <url>]"
echo "Or use interactive mode: /pi:setup --edit-config"
```

Then stop — do not proceed to setup.

### `--test` flag

When `$ARGUMENTS` includes `--test`, run a quick connectivity test:

```bash
pi -p --provider "$PROVIDER" --model "$MODEL" --thinking low --no-session --no-context-files --approve "Reply with exactly: OK. Model: <model-name>"
```

Report the result: "pi responded successfully with model <name>" on exit 0, or the error on failure.

## Setup Process

### Step 1: Detect current state

Show the user their current configuration:

```bash
echo "=== Current pi configuration ==="
if [ -f "$HOME/.claude/pi.local.json" ]; then
  cat "$HOME/.claude/pi.local.json"
else
  echo "No configuration file found."
fi
```

### Step 2: Collect configuration from CLI flags or interactive

If `$ARGUMENTS` contains flags, parse them directly:

| Flag | Description |
|------|-------------|
| `--endpoint` | Endpoint key name (default `local-proxy`) |
| `--provider` | LLM provider name (`openai`, `anthropic`, `google`, etc.) |
| `--model` | Model ID (e.g. `gemini-3.6-flash-high`, `claude-sonnet-4-20250514`) |
| `--base-url` | Custom API endpoint URL (OpenAI-compatible) |
| `--api-key` | API key for the provider (stored in settings file, or reference `$ENV_VAR`) |

If no flags are provided, use the AskUserQuestion tool to ask the user:

1. **Provider**: What provider do you want to use? (Options: `openai`, `anthropic`, `google`, or "Other" for custom)
2. **Model**: What model ID? (e.g. `gemini-3.6-flash-high`, `claude-sonnet-4-20250514`)
3. **Base URL** (optional): Custom endpoint URL, or empty for the provider's default
4. **API Key** (optional): API key or `$ENV_VAR` reference? (leave empty to use environment variables)

### Step 3: Write configuration

```bash
mkdir -p "$HOME/.claude"

# Read existing config
EXISTING="{}"
if [ -f "$HOME/.claude/pi.local.json" ]; then
  EXISTING=$(cat "$HOME/.claude/pi.local.json")
fi

# Endpoint target: an explicit --endpoint names the key to write; otherwise reconfigure
# the existing defaultEndpoint (so a plain /pi:setup reaches the endpoint the skills read).
ENDPOINT_IS_EXPLICIT="0"
if [[ "$ARGUMENTS" == *"--endpoint"* ]]; then
  ENDPOINT_IS_EXPLICIT="1"
  ENDPOINT="${ENDPOINT:-local-proxy}"
else
  ENDPOINT="${ENDPOINT:-$(echo "$EXISTING" | jq -r '.defaultEndpoint // "local-proxy"')}"
fi

# Merge into the endpoints map — only override non-empty fields.
# When an explicit --endpoint is given, make it the default so provider and model
# resolve consistently (see defaultModel note below).
echo "$EXISTING" | jq \
  --arg e "$ENDPOINT" \
  --arg explicit "${ENDPOINT_IS_EXPLICIT:-}" \
  --arg provider "${PROVIDER:-}" \
  --arg model "${MODEL:-}" \
  --arg baseUrl "${BASE_URL:-}" \
  --arg apiKey "${API_KEY:-}" \
  '.endpoints[$e] = (.endpoints[$e] // {provider: $provider}) |
   .endpoints[$e].provider = (if $provider != "" then $provider else .endpoints[$e].provider end) |
   .endpoints[$e].baseUrl = (if $baseUrl != "" then $baseUrl else .endpoints[$e].baseUrl // "" end) |
   .endpoints[$e].apiKey = (if $apiKey != "" then $apiKey else .endpoints[$e].apiKey // "" end) |
   .endpoints[$e].models = ((.endpoints[$e].models // []) + [($model | select(. != ""))] | unique) |
   .defaultEndpoint = (if $explicit == "1" then $e else (.defaultEndpoint // $e) end) |
   .defaultModel = (if $model != "" then $model else .defaultModel // "" end)' \
  > "$HOME/.claude/pi.local.json.tmp" && \
  mv "$HOME/.claude/pi.local.json.tmp" "$HOME/.claude/pi.local.json"
```

### Step 4: Verify with `--test`

Run the test automatically after writing config. pi has no `--base-url` flag — a custom endpoint goes through `~/.pi/agent/models.json`. Write it there first (idempotent: register baseUrl + model, skip when unchanged), then test:

```bash
# Ensure the endpoint is in the agent-dir models.json (pi reads endpoints from there)
# Use PROVIDER_KEY for the write so $PROVIDER (possibly empty = pi's default) is untouched.
if [ -n "$BASE_URL" ]; then
  PROVIDER_KEY="${PROVIDER:-openai}"
  mkdir -p "$HOME/.pi/agent"
  EXISTING=$(cat "$HOME/.pi/agent/models.json" 2>/dev/null || echo '{}')
  NEW=$(echo "$EXISTING" | jq -c --arg provider "$PROVIDER_KEY" --arg baseUrl "$BASE_URL" --arg model "$MODEL" \
    '.providers[$provider] = (.providers[$provider] // {}) |
     .providers[$provider].baseUrl = $baseUrl |
     if $model != "" then
       (.providers[$provider].models //= []) |
       .providers[$provider].models |= (
         if any(.id == $model) then . else . + [{id: $model}] end
       )
     else . end')
  if [ "$NEW" != "$EXISTING" ]; then
    echo "$NEW" > "$HOME/.pi/agent/models.json.tmp" && mv "$HOME/.pi/agent/models.json.tmp" "$HOME/.pi/agent/models.json"
  fi
fi

pi -p ${PROVIDER:+--provider "$PROVIDER"} --model "$MODEL" --thinking low --no-session --no-context-files --approve "Reply with exactly: OK. Model: <model-name>"
```

Report success or failure to the user.

### Step 5: Summary

Show the final configuration and tell the user:

```
pi configured successfully. Both `/pi:delegate` and `/pi:review` will use these settings by default.

To override for a single invocation:
  /pi:delegate <task> --endpoint <name> --model <id>
  /pi:review --endpoint <name> --model <id>

To edit manually:
  /pi:setup --edit-config

To view current config:
  /pi:setup --list-models
```

## Common configurations

### OpenAI-compatible endpoint (with custom base URL)

Configure an endpoint in `~/.claude/pi.local.json`:

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

Or via `/pi:setup --edit-config --global`.

### Anthropic direct

```bash
/pi:setup --endpoint anthropic-direct --provider anthropic --model claude-sonnet-4-20250514
```

### Google Gemini direct

```bash
/pi:setup --endpoint google --provider google --model gemini-3.6-flash-high
```

## References

- `/pi:delegate` — delegates coding tasks to pi
- `/pi:review` — reviews code via pi with read-only tools
- `~/.claude/pi.local.json` — global user settings (read by both delegate and review)
