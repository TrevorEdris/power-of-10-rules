# power-of-10-rules

NASA's [Power of 10 rules for developing safety-critical code][holzmann] as a Claude Code plugin: 10 per-rule skills, 2 slash commands, and 1 review subagent.

This is **not a linter**. It teaches the agent the ten rules well enough to apply them during edits, reviews, and authoring across **C, Go, Python, Java, and Kotlin**. When a hard automated check is wanted, each skill names the right existing tool to invoke (clang-tidy, golangci-lint, ruff, detekt, SpotBugs). We don't reinvent them.

## Install

```bash
/plugin marketplace add TrevorEdris/power-of-10-rules
/plugin install pow10@pow10
```

## Use

| Surface | What it does |
|---|---|
| `/pow10-overview` | Show the ten rules with severities + waiver convention |
| `/pow10-review <scope>` | Walk all ten rules over a file, dir, or `git diff` ref |
| `pow10-rule-NN-<slug>` skills | Auto-loaded when relevant code is edited or discussed |
| `pow10-auditor` agent | Same review as `/pow10-review`, run as a subagent |

## Repository layout

```
.claude-plugin/
├── plugin.json
└── marketplace.json
skills/
├── pow10-rule-01-control-flow/SKILL.md
├── pow10-rule-02-bounded-loops/SKILL.md
├── pow10-rule-03-no-dynamic-memory/SKILL.md
├── pow10-rule-04-short-functions/SKILL.md
├── pow10-rule-05-assertion-density/SKILL.md
├── pow10-rule-06-minimum-scope/SKILL.md
├── pow10-rule-07-check-return-values/SKILL.md
├── pow10-rule-08-limited-preprocessor/SKILL.md
├── pow10-rule-09-restrict-pointers/SKILL.md
└── pow10-rule-10-warnings-as-errors/SKILL.md
commands/
├── pow10-overview.md
└── pow10-review.md
agents/
└── pow10-auditor.md
```

Repo root **is** the plugin root — no nested `plugins/<tool>/` indirection.

## Waiver convention

When a rule must be broken, leave an inline comment so reviewers and future agents see it:

```
// pow10: allow rule=N until=YYYY-MM-DD owner=<handle> reason="..."
```

Use the file's native comment syntax (`//`, `#`, `--`). All four fields required. No statefile.

## Languages covered

C, Go, Python, Java, Kotlin. Each rule's per-language section gives concrete violation patterns, remediation snippets, and the existing analyzer to invoke for hard checks.

## Other AI tools

This repo currently targets Claude Code only. Cursor and Codex variants were removed in 0.2.0 to cut maintenance overhead. If interest emerges, contributors can re-add them under a `contrib/` path that mirrors the canonical Claude Code skills.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the 200-line SKILL.md size policy and the per-language split layout.

## License

MIT. See [LICENSE](LICENSE). Rule text paraphrases [Holzmann (2006)][holzmann] and the JPL Institutional Coding Standard.

[holzmann]: https://spinroot.com/gerard/pdf/P10.pdf
