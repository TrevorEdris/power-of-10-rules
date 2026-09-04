---
description: Audit a file, directory, or git ref against the NASA Power of 10 rules via the pow10-auditor agent. Usage: /pow10-review <file | dir | git-ref> [--strict]. Adapted profile by default; --strict applies the literal rules.
argument-hint: <file | dir | git-ref> [--strict]
---

Arguments: `$ARGUMENTS`

1. If the arguments end with `--strict`, remove that token and set `strict=true`; otherwise `strict=false`. What remains is `scope`. If `scope` is empty, reply `usage: /pow10-review <file | dir | git-ref> [--strict]` and stop.
2. Use the `pow10-auditor` agent with `scope=<scope>`, `strict=<strict>`, `plugin_root=${CLAUDE_PLUGIN_ROOT}`, `format=markdown`.
3. Print the agent's report verbatim. Add nothing before or after it.
