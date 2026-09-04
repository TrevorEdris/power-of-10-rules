---
name: pow10
description: Tour of the ten NASA Power of 10 rules and how this plugin adapts each for everyday Go and Python versus the literal C original, with the severity matrix and the adapted-vs-strict switch. Use when asked what the Power of 10 rules are, how pow10 interprets a rule, or which checklist to apply. Does not review code.
disable-model-invocation: true
---

# pow10 - overview

Gerard Holzmann's "Power of 10" (NASA/JPL, 2006) is ten rules for writing verifiable safety-critical C. This plugin turns them into checklists Claude applies while it writes and reviews code, without being asked.

## How activation works

- There are no hooks and no config file. Each language skill triggers on its description while Claude edits or reviews that language.
- `pow10-go` and `pow10-python` apply the **adapted** profile: the same ten hazards, interpreted for normal application code. Idiomatic code is not a violation by itself.
- `pow10-c` applies the **literal** profile: the rules as written, because C is the language they were written for.
- Say "use the strict pow10 profile", or pass `--strict` to `/pow10-review`, to get the literal rules and severities for any language. Findings are then prefixed `[STRICT]`.

## The ten rules

| # | Rule (literal, C) | Strict sev | Adapted Go | Adapted Python |
| --- | --- | --- | --- | --- |
| 1 | Simple control flow: no `goto`, `setjmp`/`longjmp`, no recursion | blocker | recursion over external input needs a depth cap [medium] | same; no `setrecursionlimit` band-aids [medium] |
| 2 | Every loop has a static upper bound | blocker | retries and polls capped or context-cancelled; server loops honor cancellation [medium] | `while True` has a max count or timeout; workers check a shutdown event [medium] |
| 3 | No heap allocation after initialization | blocker | no input-sized allocation without a bound; caches bounded [advisory] | no unbounded accumulators or caches; generators over lists [advisory] |
| 4 | Functions fit one page: 60 lines | high | `funlen` defaults, one responsibility [medium] | `PLR0915`/`PLR0912` defaults, guard clauses [medium] |
| 5 | Two runtime assertions per function on average | high | validate at trust boundaries; panic only for programmer bugs [advisory] | never `assert` for input validation; raise specific exceptions [medium] |
| 6 | Smallest possible scope; no mutable globals | medium | no package `var` mutated after init; inject state [medium] | no `global`; module names assigned once [medium] |
| 7 | Check every return value; validate every parameter | blocker | every `error` checked; entry points validate before mutating [blocker] | no bare `except`; status returns checked; `Optional` narrowed [high] |
| 8 | Limited preprocessor use | high | no `reflect` dispatch in logic; `unsafe` isolated [medium] | no `eval`/`exec`/computed `getattr` dispatch [high] |
| 9 | One level of pointer dereference; no function pointers | blocker | no `**T` APIs; dispatch maps owned by one package [medium] | dispatch dicts in one module; `Protocol` over bare `Callable` [advisory] |
| 10 | All warnings on, treated as errors; second analyzer in CI | blocker | `go vet` + `golangci-lint` fail CI; reasoned `//nolint` [high] | `ruff` + `mypy` fail CI; reasoned `# noqa` [medium] |

Severities: blocker stops the task until fixed or overridden; high and medium are reported and the task continues; advisory is listed only.

## Surfaces

| Surface | Use it for |
| --- | --- |
| `pow10-go`, `pow10-python`, `pow10-c` | Automatic. Checklist applied while writing, editing, or reviewing that language. |
| `/pow10-review <file \| dir \| git-ref> [--strict]` | Explicit review of a scope. Dispatches the agent below and prints its report. |
| `pow10-auditor` agent | The review procedure and report format. Say "audit X against the Power of 10" to dispatch it directly. |
| `/pow10` | This page. |

## Reading a finding

`pow10 R7 [blocker] internal/api/order.go:42 - discarded error from tx.Commit - check and return it`

Rule number, severity, location, what is wrong, what to do. The agent groups findings by severity under `Blockers`, `High`, `Medium`, `Advisory`.

## Where the depth lives

Each language skill keeps one reference per rule in `references/rule-NN-<slug>.md`: the canonical statement, the adapted interpretation, a checklist, a violating example, its fix, verified tooling, and what strict mode adds. Claude reads a reference only when the checklist's "read when" condition holds.

## Install and smoke test

```bash
claude --plugin-dir ~/src/github.com/TrevorEdris/power-of-10-rules
```

Then `/pow10:pow10` for this page and `/pow10:pow10-review examples/violations.go` for a sample report. Marketplace install: `/plugin marketplace add TrevorEdris/power-of-10-rules` then `/plugin install pow10@pow10`.

## Source

Holzmann, G. J. "The Power of 10: Rules for Developing Safety-Critical Code." IEEE Computer 39(6), 2006. <https://spinroot.com/gerard/pdf/P10.pdf>
