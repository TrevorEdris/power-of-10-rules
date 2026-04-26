# power-of-10-rules

NASA's [Power of 10 rules for developing safety-critical code][holzmann] as AI-agent skills for **Claude Code**, **Cursor**, and **Codex**.

This is **not a linter**. It is a skill set that teaches AI coding agents the ten rules well enough to apply them during edits, reviews, and authoring — across C, Go, Python, Java, and Kotlin. When a hard automated check is wanted, each skill names the right existing tool to invoke (clang-tidy, golangci-lint, ruff, detekt, SpotBugs, …). We don't reinvent them.

## Why a skill, not a tool

- **Multi-language, multi-tool** — same rule taught five ways, deployed to three editors
- **Zero runtime** — markdown only. No Python, Node, or build step
- **Per-language remediation guidance** — actual code patterns, not just rule statements
- **Inline waiver convention** — `// pow10: allow rule=N until=YYYY-MM-DD owner=<handle> reason="..."` parsed by the agent, not by us

## Install

### Claude Code

```bash
/plugin marketplace add TrevorEdris/power-of-10-rules
/plugin install pow10@pow10
```

Then ask the agent: `apply pow10 to this file` or `review this diff for pow10`.

### Cursor

```bash
git clone https://github.com/TrevorEdris/power-of-10-rules /tmp/pow10
mkdir -p .cursor/rules
cp /tmp/pow10/plugins/cursor/.cursor/rules/*.mdc .cursor/rules/
```

### Codex

```bash
git clone https://github.com/TrevorEdris/power-of-10-rules /tmp/pow10
cat /tmp/pow10/plugins/codex/AGENTS.pow10.md >> AGENTS.md
mkdir -p .codex/prompts
cp /tmp/pow10/plugins/codex/prompts/*.md .codex/prompts/
```

## Skills

| Skill | Purpose |
|---|---|
| `pow10-overview` | Index of the ten rules + when to apply |
| `pow10-rule-01-control-flow` | No goto, setjmp/longjmp, recursion |
| `pow10-rule-02-bounded-loops` | Every loop has a static upper bound |
| `pow10-rule-03-no-dynamic-memory` | No heap after init |
| `pow10-rule-04-short-functions` | ≤60 lines per function |
| `pow10-rule-05-assertion-density` | ≥2 runtime assertions per function |
| `pow10-rule-06-minimum-scope` | Narrow scope; no mutable globals |
| `pow10-rule-07-check-return-values` | Validate params; check returns |
| `pow10-rule-08-limited-preprocessor` | No macro/reflection abuse |
| `pow10-rule-09-restrict-pointers` | One level of indirection; no fn pointers |
| `pow10-rule-10-warnings-as-errors` | Strictest flags; second analyzer |
| `pow10-review` | Walk all ten rules over a diff/file/dir |
| `pow10-auditor` (agent) | Same review as a delegated subagent |

## Languages covered

C, Go, Python, Java, Kotlin. Each rule's per-language section gives concrete violation patterns, remediation snippets, and the relevant existing analyzer to invoke for hard checks.

## Repository layout

```
plugins/
├── claude-code/    # Claude Code plugin (skills + agents)
├── cursor/         # Cursor .mdc rules
└── codex/          # Codex AGENTS fragment + prompts
```

Each plugin is hand-maintained — no codegen. Power of 10 rules have been stable since 2006; drift risk is theoretical and tooling cost was real (the previous iteration of this repo had ~1,800 LOC of Python doing what 30 markdown files do here).

## Contributing

Triple-author policy: when changing rule content, update all three plugin directories in the same commit. PR template includes a checklist.

## License

MIT. See [LICENSE](LICENSE).

Rule text paraphrases [Holzmann (2006)][holzmann] and the JPL Institutional Coding Standard.

[holzmann]: https://spinroot.com/gerard/pdf/P10.pdf
