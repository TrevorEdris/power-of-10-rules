# Contributing

## Layout (enforced by `tools/validate.py` in CI)

```
skills/pow10-<lang>/
├── SKILL.md                       <= 200 lines; frontmatter name == directory; description contains "Use when"
└── references/
    ├── rule-01-control-flow.md    35-100 lines; exact heading set, see below
    ├── ...
    └── rule-10-warnings-as-errors.md
skills/pow10/SKILL.md              overview; disable-model-invocation: true; no references/
```

`SKILL.md` is the checklist Claude reads on trigger: announce line, when it applies, ten rules with severity and a "read when" pointer, reporting format, strict profile, rationalizations, tooling baseline.

Each reference has exactly these parts, in order:

1. `# Rule N - <Title> (<Go|Python|C>)`
2. `**Statement (Holzmann):** ...`
3. `**Profile (adapted):** applies <fully|partially|in spirit|not applicable>; severity **<blocker|high|medium|advisory>**.` (C uses `(literal)`)
4. `## Checklist` (3-6 mechanical bullets)
5. `## Violation` (one fenced block, 5-20 lines, compiles)
6. `## Fix` (one fenced block, 5-20 lines)
7. `## Tooling` (bullets starting with a backticked tool; only names in `tools/verified/`)
8. `## Strict profile` (1-4 lines)

Severities per rule and language are fixed in `tools/validate.py` (`SEVERITY`). Change them there and in `skills/pow10/SKILL.md` together.

## Hard rules

- No em dashes. No hedging ("consider", "probably").
- Never cite a linter, check, or rule code that is not in `tools/verified/`. Regenerate those lists (see `tools/verified/README.md`) before adding a new citation.
- Forbidden strings anywhere under `skills/`, `agents/`, `commands/`, `README.md`, `CONTRIBUTING.md`: the list lives in `tools/validate.py` (`FORBIDDEN`).

## Adding a language

1. Create `skills/pow10-<lang>/SKILL.md` and ten `references/rule-NN-<slug>.md` files following the shapes above.
2. Add the language to `LANGS` and a severity column to `SEVERITY` in `tools/validate.py`; add a verified tool list under `tools/verified/`.
3. Add the extension mapping to `agents/pow10-auditor.md` step 3 and a row to the overview table in `skills/pow10/SKILL.md`.
4. Run `python3 tools/validate.py` until it prints `OK`.

## Verifying locally

```bash
python3 tools/validate.py
gofmt -e -l examples/violations.go && python3 -m py_compile examples/violations.py
claude --plugin-dir .
```
