
# pow10-review — Structured Review Pass

## What this skill does

Walks the target (diff, file, or directory) once per rule, reports findings as `file:line — rule N — short description — suggested fix`. Pure prompt — no CLI to invoke. The agent does the reading.

## When to use

- Before merging a PR that touches safety-critical code
- Periodic audit of a module being onboarded into the pow10 discipline
- Spot-check after a refactor

## Procedure

1. **Determine scope.** Ask the user (or infer from context): full repo, single file, `git diff main`, or `git show <ref>`.
2. **Detect language(s)** present in scope.
3. **Load rule context.** For each of the 10 rules, load the corresponding `pow10-rule-NN-...` skill. Pull the per-language section that matches the scope.
4. **Pass per rule.** For each rule:
   - State the rule statement in one sentence
   - Scan the scope for violations matching the per-language patterns
   - Report findings: `path:line — rule N — description — suggested fix`
   - If clean: `rule N: no findings`
5. **Honor waivers.** If a violation site has an inline `pow10: allow rule=N ...` comment within ±3 lines, exclude it from findings but list it in a separate "active waivers" section. Flag any whose `until=` date has passed.
6. **Summarize.**
   - Total findings by severity (blocker / high / medium)
   - Active waivers count + expired waivers count
   - Recommended next action

## Output template

```
# pow10 review: <scope>

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

## What this skill does NOT do

- Run external linters. The user can invoke `clang-tidy`, `golangci-lint`, `ruff`, `detekt`, etc. — see each rule skill for tool names. We surface what to run, not wrap it.
- Auto-fix. Findings include suggestions; user/agent applies.
- Persist findings to disk. Output goes to the conversation.

## See also

- `pow10-overview` — rule index
- `pow10-rule-NN-...` — per-rule deep dive
- `pow10-auditor` agent — same review as a delegated subagent run
