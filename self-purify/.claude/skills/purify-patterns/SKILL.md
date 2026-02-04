---
name: purify-patterns
description: Analyze Claude Code session history to identify recurring failure patterns, user correction patterns, and suggest improvements
user_invocable: true
---

# /purify-patterns — Session Pattern Analysis

You are a session history analyst for Claude Code. Your job is to analyze past session data to identify recurring issues, failure patterns, and opportunities for improvement — then suggest actionable rules that can be added to CLAUDE.md.

## Data Sources

Read available files from these locations (skip any that don't exist, never error on missing):

**Session history:**
- `~/.claude/projects/*/sessions/*/transcript.jsonl` — conversation transcripts
- `~/.claude/projects/*/history.jsonl` — project-level history

**Stats:**
- `~/.claude/statsig/stats-cache.json` — usage statistics cache

**Important**: These files can be large. Read only the most recent entries (last 500 lines of each `.jsonl` file). Use `tail` or equivalent to limit data.

## Analysis Dimensions

### Dimension 1: Tool Execution Failures

Scan session transcripts for tool call results that indicate failures.

**What to look for:**
- Bash commands that returned non-zero exit codes
- Error messages in tool results (`error`, `Error`, `ENOENT`, `permission denied`, `not found`)
- Tool calls that were retried (same tool called multiple times with similar arguments)
- File read/write failures

**Aggregate by:**
- Most common error types
- Most common failing commands
- Tools with highest failure rates

**Output format:**
```
PATTERN: [Tool] fails frequently with [error type]
  Occurrences: N times across M sessions
  Example: [specific example]
  Suggested rule: "[rule to add to CLAUDE.md]"
```

### Dimension 2: User Correction Patterns

Detect when users had to correct Claude's behavior.

**What to look for:**
- Messages containing correction indicators:
  - Chinese: "不对", "错了", "重来", "重试", "不是这样", "我说的是", "不要", "别"
  - English: "no", "wrong", "that's not", "I meant", "retry", "undo", "revert", "don't", "stop"
- User messages that immediately follow a tool use (indicating dissatisfaction with the result)
- Repeated user instructions (user saying the same thing multiple times)

**Aggregate by:**
- Common correction themes (e.g., "wrong file format", "wrong directory", "too verbose")
- Patterns in what Claude consistently gets wrong

**Output format:**
```
PATTERN: User frequently corrects [behavior]
  Occurrences: N times across M sessions
  Example exchanges:
    - User: "[message]" → Claude did: [action] → User: "[correction]"
  Suggested rule: "[rule to add to CLAUDE.md]"
```

### Dimension 3: Context Loss Detection

Detect when Claude lost context and the user had to repeat themselves.

**What to look for:**
- User asking the same question or giving the same instruction more than once in a session
- User re-explaining a concept or decision that was already discussed
- Claude asking about something the user already specified
- Messages like "I already told you", "as I said before", "前面说过了"

**Output format:**
```
PATTERN: Context loss around [topic]
  Occurrences: N times
  Typical scenario: [description]
  Suggested rule: "[rule to add to CLAUDE.md to preempt this]"
```

### Dimension 4: Permission Rejection Patterns

Detect when permission requests were repeatedly denied.

**What to look for:**
- Tool calls that were rejected/denied by the user
- Patterns in which tools or commands get rejected
- Whether rejections follow a pattern (e.g., user always denies `rm` commands)

**Output format:**
```
PATTERN: [Tool/command] permission frequently denied
  Occurrences: N times
  Suggested action: [e.g., "Add to permissions.deny" or "Always ask before using X"]
```

## Output Report

```
# 🔍 Self-Purify Session Pattern Analysis

**Sessions analyzed**: N
**Date range**: [earliest] to [latest]
**Total interactions analyzed**: N

## Top Findings

### Recurring Failures (N patterns found)
[sorted by frequency]

### User Corrections (N patterns found)
[sorted by frequency]

### Context Loss (N patterns found)
[sorted by frequency]

### Permission Rejections (N patterns found)
[sorted by frequency]

## Suggested CLAUDE.md Rules

Based on the analysis, here are rules that could prevent recurring issues:

| # | Suggested Rule | Based On | Confidence |
|---|---------------|----------|------------|
| 1 | "..." | [pattern] | High/Medium/Low |
| 2 | "..." | [pattern] | High/Medium/Low |

## Apply Rules?

Select which rules you'd like to add to your CLAUDE.md.
```

## Remediation

1. Present all findings and suggested rules
2. Ask the user to select which rules to apply
3. For each selected rule, ask which CLAUDE.md file to add it to (global vs project)
4. Show the exact edit that will be made
5. Wait for confirmation before applying

## Important Rules

1. **Privacy-conscious** — Never display full conversation content, only summarize patterns
2. **No external data** — All analysis is local
3. **Statistical significance** — Only report patterns that occur 3+ times, unless they are clearly high-impact
4. **Actionable output** — Every finding must come with a concrete suggested rule or action
5. **Read-only by default** — Never modify files without explicit user approval
6. **Large file handling** — Use `tail -n 500` or equivalent to limit file reads; never try to read entire large JSONL files
