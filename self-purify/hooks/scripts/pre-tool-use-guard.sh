#!/usr/bin/env bash
# Self-Purify: PreToolUse Guard for Bash Commands
# Intercepts suspicious Bash commands that could exfiltrate Claude data.
# Blocking: exits 2 with reason when a threat is detected.
# Pass-through: exits 0 for safe commands.
#
# This hook receives tool input via $TOOL_INPUT environment variable
# which contains the Bash command being executed.

set -euo pipefail

# The command to be executed is passed via stdin as JSON
# Format: {"tool_name": "Bash", "tool_input": {"command": "..."}}
INPUT=$(cat)

# Extract the command from JSON input
COMMAND=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    # Handle both possible input formats
    if 'tool_input' in data:
        inp = data['tool_input']
        if isinstance(inp, dict) and 'command' in inp:
            print(inp['command'])
        elif isinstance(inp, str):
            print(inp)
        else:
            print('')
    elif 'input' in data:
        inp = data['input']
        if isinstance(inp, dict) and 'command' in inp:
            print(inp['command'])
        else:
            print(str(inp))
    else:
        print('')
except:
    print('')
" 2>/dev/null || echo "")

# If we couldn't extract a command, pass through
if [[ -z "$COMMAND" ]]; then
  exit 0
fi

# --- Guard Functions ---

# Guard 1: Claude data + POST to external URL
# Detects: cat ~/.claude/... | curl -X POST ...
check_claude_data_exfil() {
  # Check if command reads from .claude directory AND sends to network
  if echo "$COMMAND" | grep -qE '\.claude/' && \
     echo "$COMMAND" | grep -qE 'curl|wget|nc |ncat|http\.request|fetch'; then
    echo '{"error": "BLOCKED by Self-Purify: This command reads Claude data and sends it to a network endpoint. This is a potential data exfiltration attempt. If this is intentional, run the command manually outside Claude Code."}'
    exit 2
  fi
}

# Guard 2: base64 encode Claude data + network send
# Detects: cat ~/.claude/history.jsonl | base64 | curl ...
check_base64_exfil() {
  if echo "$COMMAND" | grep -qE 'base64' && \
     echo "$COMMAND" | grep -qE '\.claude|CLAUDE' && \
     echo "$COMMAND" | grep -qE 'curl|wget|nc |ncat'; then
    echo '{"error": "BLOCKED by Self-Purify: This command base64-encodes Claude data and sends it to a network endpoint. This is a potential obfuscated data exfiltration attempt."}'
    exit 2
  fi
}

# Guard 3: Environment variable harvesting + network send
# Detects: env | curl -X POST ..., printenv | base64 | curl ...
check_env_harvest() {
  if echo "$COMMAND" | grep -qE '(^|\|)\s*(env|printenv|export|compgen\s+-v|set\s)' && \
     echo "$COMMAND" | grep -qE 'curl|wget|nc |ncat'; then
    echo '{"error": "BLOCKED by Self-Purify: This command harvests environment variables and sends them to a network endpoint. Environment variables often contain API keys and secrets."}'
    exit 2
  fi
}

# Guard 4: Session history exfiltration
# Detects: cat ~/.claude/projects/*/xxx.jsonl | curl ...
check_history_exfil() {
  if echo "$COMMAND" | grep -qE '(\.jsonl|history|stats-cache|projects/)' && \
     echo "$COMMAND" | grep -qE 'curl|wget|nc |ncat' && \
     echo "$COMMAND" | grep -qE 'POST|--data|-d |--upload|-T '; then
    echo '{"error": "BLOCKED by Self-Purify: This command appears to exfiltrate Claude session history or project data to an external endpoint."}'
    exit 2
  fi
}

# Guard 5: Settings file exfiltration
# Detects: curl -d @~/.claude/settings.json https://...
check_settings_exfil() {
  if echo "$COMMAND" | grep -qE 'settings.*\.json' && \
     echo "$COMMAND" | grep -qE 'curl|wget' && \
     echo "$COMMAND" | grep -qE 'POST|--data|-d |@'; then
    echo '{"error": "BLOCKED by Self-Purify: This command appears to send Claude settings files to an external endpoint. Settings may contain sensitive configuration."}'
    exit 2
  fi
}

# Guard 6: Feishu/Lark/Slack/Discord webhook POST
# Detects: curl -X POST https://open.feishu.cn/open-apis/bot/v2/hook/...
check_webhook_post() {
  if echo "$COMMAND" | grep -qE '(open\.feishu\.cn|open\.larksuite\.com|hooks\.slack\.com|discord\.com/api/webhooks|webhook\.site|requestbin\.com)'; then
    echo '{"error": "BLOCKED by Self-Purify: This command sends data to a known webhook service (Feishu/Lark/Slack/Discord/webhook.site). This is a common data exfiltration vector."}'
    exit 2
  fi
}

# --- Run all guards ---
check_claude_data_exfil
check_base64_exfil
check_env_harvest
check_history_exfil
check_settings_exfil
check_webhook_post

# All checks passed — allow the command
exit 0
