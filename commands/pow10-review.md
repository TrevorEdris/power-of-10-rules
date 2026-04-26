---
description: Review a file, directory, or git diff against all 10 NASA Power of 10 rules. Pass scope as argument (e.g. /pow10-review src/foo.c, /pow10-review main..HEAD).
argument-hint: <file | directory | git-ref>
---

Review the following scope against all 10 NASA Power of 10 rules: $ARGUMENTS

Procedure:

1. **Resolve scope.** If $ARGUMENTS looks like a git ref (contains `..` or matches a commit), run `git diff --name-only $ARGUMENTS` to get the file list. Otherwise treat as path or glob.
2. **Detect language(s)** from extensions: `.c .h` → C; `.go` → Go; `.py` → Python; `.java` → Java; `.kt .kts` → Kotlin. Skip files in unsupported languages with a one-line note.
3. **Load rule context.** For each of the 10 rules, load the matching `pow10-rule-NN-<slug>` skill. Use the per-language section that matches the file under review.
4. **Pass per rule.** For each rule, scan the scope for violations. Report each finding as: `path:line — rule N — short description — suggested fix`.
5. **Honor waivers.** Inline `pow10: allow rule=N until=YYYY-MM-DD owner=<handle> reason="..."` within ±3 lines of a violation site masks that finding. Collect waiver records separately. Flag any whose `until` date has passed.
6. **Summarize.**
   - Counts by severity: blocker / high / medium
   - Active waivers count + expired waivers count
   - Recommended next action (fix blockers, re-evaluate expired waivers, run named external tool for hard verification)

Output format:

```
# pow10 review: $ARGUMENTS

## Summary
- blocker: <N>
- high:    <N>
- medium:  <N>
- waivers: <N> active, <N> expired

## Findings

### Rule 1 — Control Flow
- src/foo.c:42 — recursive call to `walk()`. Suggest: replace with iterative stack-based walk capped at MAX_DEPTH.

### Rule 2 — Bounded Loops
- (none)

[...]

## Waivers
- src/main.c:88 — rule=2 owner=fsw-team until=2099-01-01 reason="main event loop"

## Expired Waivers
- src/legacy.c:120 — rule=3 expired 2026-01-15
```

Boundaries:

- Do not run external linters. Surface their names in suggested fixes (clang-tidy, golangci-lint, ruff, detekt, SpotBugs).
- Do not modify code. Findings only.
- Do not exclude valid waivers from output — list them so reviewers see active suppressions.
- If scope is empty or unreadable, report that and stop.

Tone: terse. One line per finding. Reader is a senior engineer.
