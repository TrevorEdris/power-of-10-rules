# Contributing

## SKILL.md size limit

**Hard limit: 200 lines per SKILL.md.**

When a per-rule SKILL.md exceeds 200 lines, split per-language sections into reference files using progressive disclosure:

```
skills/pow10-rule-NN-<slug>/
├── SKILL.md                 # rule statement, rationale, universal patterns,
│                            # context-manifest pointing at language refs
└── references/
    ├── c.md
    ├── go.md
    ├── python.md
    ├── java.md
    └── kotlin.md
```

`SKILL.md` keeps:

- Frontmatter (`name`, `description`)
- Rule statement, severity, rationale
- Universal violation patterns + remediation example
- Waiver convention reference
- Citations
- A `context-manifest` block listing the per-language references

`references/<lang>.md` carries:

- Language-specific forbidden patterns
- Language-specific replacement idioms
- Tool names + check codes (clang-tidy, golangci-lint, ruff, detekt, SpotBugs)
- Language-specific remediation examples

The agent loads only the language references relevant to the file under review.

CI enforces the 200-line limit — see `.github/workflows/ci.yml`.

## Adding a language

Today: C, Go, Python, Java, Kotlin. To add another:

1. Append a per-language section to every rule's SKILL.md (or a `references/<lang>.md` file if that rule already exceeds 200 lines).
2. Update `commands/pow10-overview.md` if the languages list is mentioned.
3. Update `README.md` "Languages covered" line.

## Citations

Rule wording paraphrases Holzmann (2006) and the JPL Institutional Coding Standard. Don't quote either verbatim at length — paraphrase, then cite.
