# Self-Purify Plugin

This plugin provides security auditing and configuration optimization for Claude Code.

## Available Commands

- `/purify` — Run all three modules in sequence and produce a unified report
- `/purify-audit` — Security audit: scan for leaked keys, malicious plugins, unsafe hooks
- `/purify-claudemd` — CLAUDE.md optimization: detect duplicates, contradictions, stale references
- `/purify-patterns` — Session analysis: identify recurring failures and correction patterns

## Design Principles

- **Completely local** — No data is ever sent externally
- **Read-only by default** — All changes require explicit user confirmation
- **Transparent** — All detection logic is in readable markdown and shell scripts
- **Self-safe** — This plugin does not introduce the vulnerabilities it detects

## Hooks

This plugin installs two hooks:
1. **SessionStart**: Lightweight security scan on every session start (non-blocking, warn only)
2. **PreToolUse (Bash)**: Guards against data exfiltration commands (blocking on detection)
