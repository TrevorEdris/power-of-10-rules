# power-of-10-rules

NASA's Power of 10 rules for safety-critical code, packaged as a Claude Code plugin that applies them while Claude writes and reviews Go, Python, and C. No hooks, no config: three language skills trigger on their descriptions; one command and one agent handle explicit reviews.

## Install

Local checkout:

```bash
claude --plugin-dir ~/src/github.com/TrevorEdris/power-of-10-rules
```

Marketplace:

```
/plugin marketplace add TrevorEdris/power-of-10-rules
/plugin install pow10@pow10
```

## What you get

| Surface | Behavior |
| --- | --- |
| `pow10-go`, `pow10-python` | Trigger while writing, editing, or reviewing that language. Ten-item checklist, **adapted** for normal application code. |
| `pow10-c` | Same, with the rules in their original literal form. C is the canonical reference. |
| `/pow10-review <scope> [--strict]` | Explicit review of a file, directory, or git ref. Dispatches `pow10-auditor` and prints its report. |
| `pow10-auditor` agent | Owns the review procedure and the report format (findings grouped by blocker / high / medium / advisory). |
| `/pow10` | Overview: the ten rules, the severity matrix, adapted vs strict. |

Adapted is the default everywhere except C. Ask for "the strict pow10 profile" or pass `--strict` to get the literal rules and severities for any language.

## Smoke test

```
/pow10:pow10
/pow10:pow10-review examples/violations.go
/pow10:pow10-review examples/violations.py --strict
```

Then edit a Go or Python file in any project and watch for `Using pow10-go ...` / `Using pow10-python ...` in Claude's first line.

## Repository layout

```
.claude-plugin/          plugin.json, marketplace.json (repo root is the plugin root)
skills/pow10/            overview skill (user-invocable only)
skills/pow10-go/         SKILL.md checklist + references/rule-01..10-<slug>.md
skills/pow10-python/     same
skills/pow10-c/          same
agents/pow10-auditor.md  review procedure + report format
commands/pow10-review.md thin dispatcher
examples/                violation fixtures for the smoke test
tools/validate.py        structural validator (run in CI); tools/verified/ = tool-name snapshots
```

## Languages

Go and Python are primary and get the adapted profile. C is the canonical literal reference. Nothing else is supported; see [CONTRIBUTING.md](CONTRIBUTING.md) to add a language.

## Source

Holzmann, G. J. "The Power of 10: Rules for Developing Safety-Critical Code." IEEE Computer 39(6), 2006. <https://spinroot.com/gerard/pdf/P10.pdf>

## License

MIT. See [LICENSE](LICENSE).
