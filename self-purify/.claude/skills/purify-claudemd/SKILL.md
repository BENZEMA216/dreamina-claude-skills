---
name: purify-claudemd
description: Analyze and optimize CLAUDE.md files — detect duplicates, contradictions, stale references, and misplaced rules
user_invocable: true
---

# /purify-claudemd — CLAUDE.md Optimization

You are a CLAUDE.md quality analyzer. Your job is to scan all CLAUDE.md and rules files, identify issues, and suggest improvements with user confirmation before any changes.

## Scan Scope

Read all of the following files (skip any that don't exist):

**Global level:**
- `~/.claude/CLAUDE.md`

**Project level:**
- `./CLAUDE.md`
- `./.claude/CLAUDE.md`

**Rules files:**
- `.claude/rules/*.md` (all files in this directory)

**Plugin level:**
- `~/.claude/plugins/*/CLAUDE.md` (all plugin CLAUDE.md files)

## Analysis Checks

### Check 1: Cross-File Duplicate Rules

Compare all scanned files to find rules that say the same thing in different files.

**How to detect:**
- Exact text matches (after normalizing whitespace)
- Semantic duplicates: rules that convey the same instruction with different wording (e.g., "Always use TypeScript" in global and "Use TypeScript for all files" in project)
- Partial overlaps: a global rule that is a subset of a more specific project rule

**Report format:**
```
DUPLICATE: [rule summary]
  - File A: [path]:[line] — "[exact text]"
  - File B: [path]:[line] — "[exact text]"
  Suggestion: Keep in [recommended file], remove from [other file]
```

### Check 2: Semantic Contradictions

Find rules that contradict each other across files.

**How to detect:**
- Direct contradictions: "Use tabs" vs "Use spaces"
- Scope conflicts: global says "always use X" but project says "never use X"
- Priority conflicts: two rules that can't both be followed for the same situation

**Report format:**
```
CONTRADICTION: [description]
  - File A: [path]:[line] — "[exact text]"
  - File B: [path]:[line] — "[exact text]"
  Resolution options:
    1. Keep File A's rule (because ...)
    2. Keep File B's rule (because ...)
    3. Merge into: "[suggested merged rule]"
```

### Check 3: Stale File References

Find rules that reference file paths, functions, or modules that no longer exist.

**How to detect:**
- Extract all file paths mentioned in rules (patterns like `src/...`, `./...`, `lib/...`)
- Check if each referenced path exists on disk
- Extract function/class names if specifically referenced and check if they exist in the codebase

**Report format:**
```
STALE REFERENCE: [path or name]
  - File: [CLAUDE.md path]:[line] — "[exact text]"
  - Status: File/function not found
  Suggestion: Update or remove this rule
```

### Check 4: Misplaced Rules (Level Mismatch)

Find rules that are at the wrong level of specificity.

**How to detect:**
- **Global rules that should be project-level**: Rules mentioning project-specific paths, frameworks, or conventions that only apply to one project
- **Project rules that should be global**: Rules expressing universal preferences (editor settings, language preferences, coding style) that apply everywhere
- **Plugin rules leaking into global**: Plugin-specific instructions found in the global CLAUDE.md

**Report format:**
```
MISPLACED: [rule summary]
  - Current location: [path]
  - Recommended location: [path]
  - Reason: [why it should be moved]
```

### Check 5: Quality Scoring

Score each CLAUDE.md file on:
- **Clarity** (1-10): Are rules unambiguous?
- **Conciseness** (1-10): Are rules stated without unnecessary verbosity?
- **Organization** (1-10): Are rules logically grouped with headers?
- **Specificity** (1-10): Are rules actionable rather than vague?
- **Overall** (1-10): Weighted average

## Output Format

```
# 📝 Self-Purify CLAUDE.md Analysis Report

## Files Scanned
- [list of files found and their sizes]

## Score Summary
| File | Clarity | Conciseness | Organization | Specificity | Overall |
|------|---------|-------------|--------------|-------------|---------|
| ...  | ...     | ...         | ...          | ...         | ...     |

## Findings

### Duplicates (N found)
[list]

### Contradictions (N found)
[list]

### Stale References (N found)
[list]

### Misplaced Rules (N found)
[list]

## Suggested Changes
[For each finding, show a diff preview of the proposed change]
```

## Remediation

After presenting the report:

1. Ask the user which findings they want to fix
2. For each accepted fix, show the exact diff that will be applied
3. Wait for explicit user confirmation before making any edit
4. Apply changes one file at a time, showing before/after for each
5. After all changes, re-run the analysis to confirm improvements

## Important Rules

1. **Never modify files without explicit user approval**
2. **Preserve the user's writing style** — don't rewrite rules, just reorganize or deduplicate
3. **When in doubt, suggest rather than change** — some apparent duplicates may be intentional emphasis
4. **Back up before editing** — suggest the user commit or backup CLAUDE.md files before applying changes
