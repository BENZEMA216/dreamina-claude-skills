# Threat Model for Claude Code Configuration

## Attack Surface

### 1. Settings Files (`settings*.json`)

**Threat**: Injected configuration that grants excessive permissions or connects to attacker-controlled services.

- `permissions.allow` can whitelist arbitrary Bash commands, including network exfiltration
- `mcpServers` can point to attacker-controlled binaries that intercept all tool calls
- `settings.local.json` overrides `settings.json` and may contain locally-injected malicious config

**Attack vector**: A malicious plugin, shared project config, or social engineering ("paste this into your settings") can inject entries.

### 2. MCP Servers

**Threat**: A malicious MCP server binary acts as a man-in-the-middle for all Claude tool calls.

- Can intercept file reads, code execution, and user data
- Can silently modify tool results
- Can exfiltrate data through its own network connections
- Runs as a long-lived subprocess with the user's full permissions

**Attack vector**: `npx` one-liner in settings that downloads and runs a malicious package, or a local binary replaced via symlink.

### 3. Hooks

**Threat**: Hook scripts execute on every tool call, session start, or other events with no sandboxing.

- `PreToolUse` hooks see every command before execution
- `PostToolUse` hooks see every result after execution
- `SessionStart` hooks run on every new session
- Hooks can silently exfiltrate data, modify behavior, or install persistence

**Attack vector**: A plugin registers hooks that appear benign but contain obfuscated exfiltration logic.

### 4. Plugins

**Threat**: Plugins have broad access through skills, hooks, and CLAUDE.md instructions.

- Skills can instruct Claude to execute arbitrary commands
- Plugin CLAUDE.md can override safety behaviors
- Plugin hooks run with user privileges
- A plugin can modify other plugins or Claude's own configuration

**Attack vector**:
- **capability-evolver pattern**: A plugin that instructs Claude to install additional capabilities, creating a self-reinforcing loop
- **Data harvesting**: Skills that instruct Claude to read environment variables, API keys, or session history and send them to external webhooks
- **Feishu/Lark exfiltration**: Sending collected data to Feishu bot webhooks (`open.feishu.cn`)

### 5. CLAUDE.md Files

**Threat**: Prompt injection through CLAUDE.md files that alter Claude's behavior.

- Can instruct Claude to skip security checks
- Can instruct Claude to ignore user requests
- Can inject hidden instructions that conflict with user intent
- Project-level CLAUDE.md can override user-level safety rules

**Attack vector**: A cloned repo contains a malicious `.claude/CLAUDE.md` or `CLAUDE.md` that hijacks Claude's behavior.

### 6. Session History

**Threat**: Session history files contain sensitive data that can be exfiltrated.

- `.jsonl` files in `~/.claude/projects/` contain full conversation transcripts
- May include code, credentials, business logic, and personal information
- `stats-cache.json` reveals usage patterns

**Attack vector**: A hook or plugin reads history files and sends them to an external endpoint.

## Attacker Profiles

### Profile A: Malicious Plugin Author
- Distributes a plugin with hidden exfiltration capabilities
- Uses obfuscation (base64, hex encoding) to hide malicious payloads
- Targets env variables and API keys

### Profile B: Supply Chain Attacker
- Compromises a popular MCP server package on npm
- Inserts data collection in an update
- Affects all users who run `npx` with the package

### Profile C: Social Engineering
- Convinces user to paste malicious config into settings
- Provides "helpful" CLAUDE.md content with hidden instructions
- Shares project repos with weaponized `.claude/` directories

## Detection Priorities

1. **Immediate data exfiltration** (Critical) — Any path from sensitive data to network egress
2. **Persistence mechanisms** (Critical) — Self-modifying plugins, auto-installing hooks
3. **Credential exposure** (Critical) — Plaintext API keys, tokens in config files
4. **Excessive permissions** (High) — Overly broad Bash wildcards, unrestricted tool access
5. **Untrusted executables** (High) — MCP servers from temp dirs, unsigned binaries
6. **Suspicious patterns** (Medium) — Obfuscated code, unusual file access patterns
7. **Configuration hygiene** (Low) — Unused entries, deprecated settings
