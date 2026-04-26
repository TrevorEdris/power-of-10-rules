# NASA Power of 10 — Codex Instruction Fragment

Append this fragment to your repository's `AGENTS.md`. Codex will load it automatically on every run.

---

## Power of 10 Compliance

This codebase follows the NASA Power of 10 rules for safety-critical code (Holzmann 2006). When writing or reviewing code:

1. **Restrict control flow** — no `goto`, no `setjmp`/`longjmp`, no recursion (direct or indirect)
2. **Bounded loops** — every loop has a statically determinable upper bound
3. **No dynamic memory after init** — heap allocation only during initialization
4. **Short functions** — ≤60 lines per function
5. **Assertion density** — average ≥2 runtime assertions per function
6. **Minimum scope** — declare data at narrowest scope; no mutable globals
7. **Check return values & validate parameters** — at every function boundary
8. **Limited preprocessor / metaprogramming** — `#include` + simple macros only; analogous restraint on reflection / codegen in other languages
9. **Restrict indirection** — at most one pointer level; no function pointers (or analogous lambda chains across module boundaries)
10. **Warnings as errors** — strictest compiler/linter flags; second analyzer in CI

When violating a rule is necessary, leave an inline comment so reviewers and future agents can find it:

```
// pow10: allow rule=N until=YYYY-MM-DD owner=<handle> reason="..."
```

Per-rule guidance with per-language examples lives in `prompts/pow10-rule-NN-...md`. Load the relevant prompt when reviewing or writing safety-critical code.

For a full review of a diff or file, load `prompts/pow10-review.md`.
