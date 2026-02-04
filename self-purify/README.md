# Self-Purify: Claude Code Self-Purification Plugin

A fully local, transparent, human-in-the-loop security and configuration hygiene tool for Claude Code.

## What It Does

Self-Purify inverts the concept of a malicious "capability-evolver" plugin — instead of expanding attack surface, it audits and hardens your Claude Code setup.

### Three Modules

| Module | Command | Purpose |
|--------|---------|---------|
| Security Audit | `/purify-audit` | Detect leaked API keys, malicious plugins, unsafe hooks, suspicious MCP servers |
| CLAUDE.md Optimizer | `/purify-claudemd` | Find duplicate rules, contradictions, stale references, misplaced rules |
| Session Analyzer | `/purify-patterns` | Identify recurring failures, user correction patterns, context loss |
| **Full Suite** | `/purify` | Run all three in sequence |

### Automatic Protection (Hooks)

- **Session Start Scan**: Quick check on every session start for obvious issues (non-blocking)
- **PreToolUse Guard**: Blocks Bash commands that attempt to exfiltrate Claude data to external endpoints

## Installation

The plugin is located at `~/.claude/plugins/self-purify/`. Claude Code should automatically detect it.

## Security Model

This plugin is designed to **not introduce the vulnerabilities it detects**:

- No network access — all operations are local
- No self-modification — the plugin never alters its own files
- No permission escalation — operates within existing Claude Code permissions
- No obfuscation — all logic is in readable shell scripts and markdown
- Human-in-the-loop — never modifies user files without explicit confirmation

## What It Detects

### Security Audit Detects:
- Plaintext API keys (OpenAI, Anthropic, GitHub, GitLab, AWS, Google, Slack)
- Webhook URLs (Feishu/Lark, Slack, Discord, webhook.site, requestbin)
- MCP servers from untrusted locations (`/tmp/`, `~/Downloads/`)
- Hooks with network commands
- Plugins with capability-evolver patterns (self-replication, env harvesting, data exfiltration)
- Overly broad Bash permission wildcards

### PreToolUse Guard Blocks:
- `cat ~/.claude/... | curl ...` (Claude data piped to network)
- `env | base64 | curl ...` (environment variable harvesting)
- `curl -X POST https://open.feishu.cn/...` (Feishu webhook exfiltration)
- Any command combining Claude data reads with network sends

## File Structure

```
~/.claude/plugins/self-purify/
├── .claude-plugin/
│   └── plugin.json                    # Plugin manifest
├── .claude/
│   └── skills/
│       ├── purify/                    # Unified /purify command
│       │   └── SKILL.md
│       ├── purify-audit/              # Security audit module
│       │   ├── SKILL.md
│       │   └── references/
│       │       ├── threat-model.md
│       │       └── known-malicious-patterns.md
│       ├── purify-claudemd/           # CLAUDE.md optimizer
│       │   └── SKILL.md
│       └── purify-patterns/           # Session pattern analyzer
│           └── SKILL.md
├── hooks/
│   ├── hooks.json                     # Hook configuration
│   └── scripts/
│       ├── session-start-scan.sh      # Session start security scan
│       └── pre-tool-use-guard.sh      # Bash command guard
├── CLAUDE.md                          # Plugin instructions
└── README.md                          # This file
```

## License

Local-use only. Not intended for distribution.
