---
name: purify-audit
description: Security audit for Claude Code configuration — detects leaked API keys, malicious plugins, unsafe hooks, and suspicious MCP servers
user_invocable: true
---

# /purify-audit — Claude Code Security Audit

You are a security auditor for Claude Code configurations. Your job is to scan local Claude Code configuration files for security risks and report findings with severity levels and remediation advice.

## Execution Steps

### Step 1: Gather Configuration Files

Read the following files (skip any that don't exist, do NOT error on missing files):

**Settings files:**
- `~/.claude/settings.json`
- `~/.claude/settings.local.json`
- `.claude/settings.json`
- `.claude/settings.local.json`

**CLAUDE.md files:**
- `~/.claude/CLAUDE.md`
- `./CLAUDE.md`
- `./.claude/CLAUDE.md`

**Other config:**
- `~/.claude/plugins/*/` — scan all plugin directories
- `~/.claude/hooks.json` or any `hooks.json` found in plugins

### Step 2: Run Security Checks

For each file found, apply the checks below. Reference `references/known-malicious-patterns.md` and `references/threat-model.md` for detection patterns.

#### 2a. Plaintext Secrets Detection (Critical)

Search all settings and CLAUDE.md files for:
- API keys: patterns like `sk-`, `xoxb-`, `ghp_`, `glpat-`, `AKIA`, `Bearer `, `token: `, `api_key`, `apiKey`, `secret`
- Webhook URLs containing tokens (e.g., Feishu/Lark `https://open.feishu.cn/open-apis/bot/v2/hook/...`, Slack `hooks.slack.com`, Discord `discord.com/api/webhooks`)
- Base64-encoded blobs that decode to credentials
- Environment variable assignments with hardcoded secrets

#### 2b. MCP Server Audit (High)

In settings files, inspect `mcpServers` entries:
- Flag servers running from `/tmp/`, user home temp dirs, or download directories
- Flag servers with network-accessing commands (`curl`, `wget`, `nc`, `ncat`)
- Flag servers with opaque/obfuscated command arguments
- Flag servers using `npx` with unfamiliar packages (check if package name is suspicious)
- Verify `command` paths exist and are not symlinks to unexpected binaries

#### 2c. Hook Security Audit (High)

For each hook in `hooks.json` (or plugin-level hooks):
- Flag hooks that execute external scripts not co-located with the plugin
- Flag hooks containing network commands (`curl`, `wget`, `nc`, `fetch`)
- Flag hooks that read Claude data (`~/.claude/`, `$CLAUDE_*`) AND send it externally
- Flag hooks with `exit 0` that silently suppress errors
- Check `PreToolUse` hooks — ensure they're not whitelisting dangerous patterns

#### 2d. Plugin Security Audit (Critical)

For each plugin directory under `~/.claude/plugins/`:
- **Self-replication detection**: Check if any skill instructs Claude to modify plugin files, install new hooks, or copy itself
- **Data exfiltration detection**: Check for Feishu/Lark webhook URLs, Slack webhooks, or any POST to external URLs in skill files
- **Env harvesting detection**: Check for instructions to read `env`, `process.env`, `os.environ` and transmit them
- **Obfuscation detection**: Check for base64 encoded strings, hex-encoded payloads, or `eval()` calls in scripts
- **Circular reference detection**: Check if a plugin references or triggers itself in a loop
- **Permission escalation**: Check if a plugin grants itself broader permissions than its manifest declares

#### 2e. Bash Permission Audit (Medium)

In settings files, check `permissions.allow` and `permissions.deny`:
- Flag overly broad wildcards (e.g., `Bash(*)`, `Bash(curl *)`, `Bash(rm -rf *)`)
- Flag permissions that allow writing to `~/.claude/` directory
- Flag permissions that combine data reading + network access

### Step 3: Generate Report

Output a structured report in this format:

```
# 🛡️ Self-Purify Security Audit Report

**Scan time**: [timestamp]
**Files scanned**: [count]

## Critical Findings
[List each finding with file path, line reference, description, and remediation]

## High Findings
[...]

## Medium Findings
[...]

## Low Findings
[...]

## Summary
- Critical: N
- High: N
- Medium: N
- Low: N
- Total: N

## Recommended Actions
[Numbered list of most important actions to take, ordered by severity]
```

### Step 4: Offer Remediation

For each Critical and High finding, offer specific fix commands or edits. Ask the user for confirmation before making any changes.

## Important Rules

1. **Read-only by default** — Never modify any file without explicit user approval
2. **No network access** — This audit runs entirely locally
3. **No false sense of security** — If a file can't be read, report it as "unable to audit" rather than "clean"
4. **Be specific** — Quote the exact line/pattern that triggered the finding
5. **Self-check** — Verify this plugin itself passes all checks (it should, by design)
