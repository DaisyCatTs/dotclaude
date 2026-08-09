# pi Doctor — Configuration Verification

Run this script when `/pi:delegate --doctor` is invoked. It checks installation, config files, effective config, and connectivity.

```bash
echo "=== pi Doctor ==="
echo ""

# 1. Check installation
echo "1. pi installation:"
if command -v pi >/dev/null 2>&1; then
  echo "   [OK] pi $(pi --version 2>&1 | head -1) at $(command -v pi)"
else
  echo "   [FAIL] pi not installed"
fi

# 2. Check config files
echo ""
echo "2. Config files:"
for f in "$HOME/.claude/pi.local.json" ".claude/pi.json" ".claude/pi.local.json"; do
  if [ -f "$f" ]; then
    echo "   [OK] $f"
  else
    echo "   [MISSING] $f (not present)"
  fi
done

# 3. Show effective config (resolved with env)
echo ""
echo "3. Effective config (resolved):"
echo "   Provider: ${PROVIDER:-pi default}"
echo "   Model: ${MODEL:-pi default}"
echo "   Base URL: ${BASE_URL:-not set}"
echo "   API Key: ${API_KEY:+set (${#API_KEY} chars)}"
echo "   Thinking: ${THINKING:-max}"

# 4. Test connectivity
echo ""
echo -n "4. Connectivity test: "
# Resolve the agent dir the same way pi-agent does (matches AGENT_DIR / PI_CODING_AGENT_DIR).
AGENT_DIR="${AGENT_DIR:-${PI_CODING_AGENT_DIR:-$HOME/.pi/agent}}"
if [ -n "$BASE_URL" ]; then
  mkdir -p "$AGENT_DIR"
  EXISTING=$(cat "$AGENT_DIR/models.json" 2>/dev/null || echo '{}')
  echo "$EXISTING" | jq --arg provider "${PROVIDER:-openai}" \
    --arg baseUrl "$BASE_URL" \
    '.providers[$provider] = (.providers[$provider] // {}) |
     .providers[$provider].baseUrl = $baseUrl' \
    > "$AGENT_DIR/models.json.tmp" && \
    mv "$AGENT_DIR/models.json.tmp" "$AGENT_DIR/models.json"
fi

TEST_OUTPUT=$(pi -p --provider "${PROVIDER:-openai}" --model "${MODEL:-gemini-3.6-flash-high}"${API_KEY:+ --api-key "$API_KEY"} --thinking low --no-session --no-context-files --approve "Reply with exactly: OK" 2>&1)
TEST_EXIT=$?
if [ "$TEST_EXIT" -eq 0 ] && echo "$TEST_OUTPUT" | grep -q "OK"; then
  echo "[OK] pi responded successfully"
else
  echo "[FAIL] pi failed (exit $TEST_EXIT):"
  echo "   $TEST_OUTPUT" | head -3
fi
```