# Contributing

## Skill layout (mandatory)

Every per-rule skill follows the split layout:

```
skills/pow10-rule-NN-<slug>/
├── SKILL.md
└── references/
    ├── c.md
    ├── go.md
    ├── python.md
    ├── java.md
    └── kotlin.md
```

`SKILL.md` carries:

- Frontmatter (`name`, `description`)
- Rule statement, severity, rationale
- Universal violation patterns (language-agnostic)
- Universal remediation pattern (language-agnostic)
- Pointers to each `references/<lang>.md`
- Waiver convention reference
- Citations

`references/<lang>.md` carries:

- Language-specific forbidden patterns
- **At least one violating code example**
- **At least one remediation step for that example**
- Tool names and check codes (clang-tidy, golangci-lint, ruff, detekt, SpotBugs)

The agent loads only the language reference relevant to the file under review, keeping context focused.

## Hard limits

- `SKILL.md` ≤ 200 lines (CI-enforced)
- Every per-rule skill MUST have all five `references/<lang>.md` files (CI-enforced)

## Adding a language

To add a new language (say, Rust):

1. Add `references/rust.md` to every per-rule skill (10 files).
2. Add a pointer line under "Per-language guidance" in each `SKILL.md`.
3. Update `commands/pow10-overview.md` and `README.md` "Languages covered" line.
4. Update CI's per-language verification step.

## Citations

Rule wording paraphrases Holzmann (2006) and the JPL Institutional Coding Standard. Don't quote either verbatim at length — paraphrase, then cite.
