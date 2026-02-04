---
name: purify
description: Run all Self-Purify modules — security audit, CLAUDE.md optimization, and session pattern analysis — in sequence
user_invocable: true
---

# /purify — Full Self-Purification

You are running the complete Self-Purify suite. Execute all three modules in order and produce a unified report.

## Execution Order

### Phase 1: Security Audit (Critical — run first)

Execute the `/purify-audit` skill fully. This is the highest priority because security issues should be addressed before anything else.

Perform all checks described in the purify-audit skill:
1. Scan settings files for plaintext secrets
2. Audit MCP servers for untrusted sources
3. Audit hooks for network access and data exfiltration
4. Audit plugins using the known-malicious-patterns reference
5. Check Bash permissions for overly broad wildcards

Collect all findings into the unified report.

### Phase 2: CLAUDE.md Optimization

Execute the `/purify-claudemd` skill fully:
1. Scan all CLAUDE.md and rules files
2. Check for duplicates, contradictions, stale references, misplaced rules
3. Score each file

Collect all findings into the unified report.

### Phase 3: Session Pattern Analysis

Execute the `/purify-patterns` skill fully:
1. Analyze recent session history
2. Detect failure patterns, user corrections, context loss, permission rejections
3. Generate suggested CLAUDE.md rules

Collect all findings into the unified report.

## Unified Report Format

```
# 🛡️ Self-Purify Complete Report

**Run time**: [timestamp]

---

## Phase 1: Security Audit

[Full audit report from purify-audit]

---

## Phase 2: CLAUDE.md Quality

[Full report from purify-claudemd]

---

## Phase 3: Session Patterns

[Full report from purify-patterns]

---

## Executive Summary

| Category | Critical | High | Medium | Low |
|----------|----------|------|--------|-----|
| Security | N | N | N | N |
| CLAUDE.md | - | N | N | N |
| Patterns | - | N | N | N |

## Top Priority Actions

1. [Most critical action, from security audit]
2. [Second most critical action]
3. [Third most critical action]
...

## Would you like to apply fixes?

I can help with:
- Fix security issues (from Phase 1)
- Optimize CLAUDE.md files (from Phase 2)
- Add suggested rules (from Phase 3)

Please tell me which items you'd like to address.
```

## Rules

1. **Run phases sequentially** — Phase 1 must complete before Phase 2
2. **Stop on critical security findings** — If Phase 1 finds Critical issues, alert the user prominently before continuing
3. **Don't apply any fixes automatically** — Present the full report first, then ask what to fix
4. **Be concise in the unified report** — If a phase has no findings, say "No issues found" rather than showing empty tables
