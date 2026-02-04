#!/usr/bin/env bash
# Self-Purify: Session Start Security Scan
# Runs on every Claude Code session start.
# Performs a lightweight (<5s) scan for obvious security issues.
# Non-blocking: always exits 0, only prints warnings.

set -euo pipefail

CLAUDE_DIR="${HOME}/.claude"
WARNINGS=()

# --- Helper ---
add_warning() {
  WARNINGS+=("$1")
}

# --- Check 1: Plaintext API keys in settings files ---
check_settings_secrets() {
  local files=(
    "${CLAUDE_DIR}/settings.json"
    "${CLAUDE_DIR}/settings.local.json"
    ".claude/settings.json"
    ".claude/settings.local.json"
  )

  local patterns=(
    'sk-[a-zA-Z0-9]\{20,\}'
    'sk-ant-[a-zA-Z0-9-]\{20,\}'
    'xoxb-[0-9]\{10,\}'
    'ghp_[a-zA-Z0-9]\{30,\}'
    'glpat-[a-zA-Z0-9-]\{20,\}'
    'AKIA[0-9A-Z]\{16\}'
  )

  for file in "${files[@]}"; do
    if [[ -f "$file" ]]; then
      for pattern in "${patterns[@]}"; do
        if grep -qE "$pattern" "$file" 2>/dev/null; then
          add_warning "[CRITICAL] Possible API key found in $file — run /purify-audit for details"
          break 2
        fi
      done
    fi
  done
}

# --- Check 2: Suspicious webhook URLs ---
check_webhook_urls() {
  local files=(
    "${CLAUDE_DIR}/settings.json"
    "${CLAUDE_DIR}/settings.local.json"
    ".claude/settings.json"
    ".claude/settings.local.json"
  )

  local webhook_patterns=(
    'open\.feishu\.cn'
    'open\.larksuite\.com'
    'hooks\.slack\.com/services'
    'discord\.com/api/webhooks'
    'webhook\.site'
    'requestbin\.com'
  )

  for file in "${files[@]}"; do
    if [[ -f "$file" ]]; then
      for pattern in "${webhook_patterns[@]}"; do
        if grep -qE "$pattern" "$file" 2>/dev/null; then
          add_warning "[HIGH] Suspicious webhook URL found in $file — run /purify-audit for details"
          break 2
        fi
      done
    fi
  done
}

# --- Check 3: MCP servers from temp directories ---
check_mcp_temp_dirs() {
  local files=(
    "${CLAUDE_DIR}/settings.json"
    "${CLAUDE_DIR}/settings.local.json"
  )

  for file in "${files[@]}"; do
    if [[ -f "$file" ]]; then
      if grep -qE '"/tmp/|"/var/tmp/|~/Downloads/' "$file" 2>/dev/null; then
        add_warning "[HIGH] MCP server binary in temp/download directory found in $file"
      fi
    fi
  done
}

# --- Check 4: Hooks with network commands ---
check_hook_network() {
  local hook_files=()

  # Find all hooks.json files in plugins
  if [[ -d "${CLAUDE_DIR}/plugins" ]]; then
    while IFS= read -r -d '' f; do
      hook_files+=("$f")
    done < <(find "${CLAUDE_DIR}/plugins" -name "hooks.json" -print0 2>/dev/null)
  fi

  # Also check top-level hooks
  if [[ -f "${CLAUDE_DIR}/hooks.json" ]]; then
    hook_files+=("${CLAUDE_DIR}/hooks.json")
  fi

  for file in "${hook_files[@]}"; do
    # Skip our own hooks.json
    if [[ "$file" == *"self-purify"* ]]; then
      continue
    fi
    if grep -qE 'curl|wget|nc |ncat|fetch' "$file" 2>/dev/null; then
      add_warning "[HIGH] Hook with network command detected in $file — run /purify-audit for details"
    fi
  done
}

# --- Run all checks ---
check_settings_secrets
check_webhook_urls
check_mcp_temp_dirs
check_hook_network

# --- Output warnings ---
if [[ ${#WARNINGS[@]} -gt 0 ]]; then
  echo ""
  echo "⚠️  Self-Purify: Security issues detected during startup scan"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  for warning in "${WARNINGS[@]}"; do
    echo "  $warning"
  done
  echo ""
  echo "  Run /purify-audit for a full security audit with remediation steps."
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
fi

# Always exit 0 — warn only, never block session start
exit 0
