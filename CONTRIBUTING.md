# Contributing

## Triple-author policy

When changing rule content, update all three plugin directories in the same commit:

- `plugins/claude-code/skills/<skill>/SKILL.md`
- `plugins/cursor/.cursor/rules/<skill>.mdc`
- `plugins/codex/prompts/<skill>.md`

The Cursor and Codex variants share body content with the Claude Code SKILL.md; only frontmatter differs. Hand-sync — no codegen.

## SKILL.md size limit

**Hard limit: 200 lines per SKILL.md.**

When a per-rule SKILL.md exceeds 200 lines, split per-language sections into reference files using progressive disclosure:

```
plugins/claude-code/skills/pow10-rule-NN-<slug>/
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
- Tool names + check codes (clang-tidy, golangci-lint, ruff, detekt, …)
- Language-specific remediation examples

The agent loads only the language references relevant to the file under review.

Mirror the same split into `plugins/cursor/.cursor/rules/<skill>/` and `plugins/codex/prompts/<skill>/` with their respective frontmatter conventions.

CI enforces the 200-line limit — see `.github/workflows/ci.yml`.

## When to add a language

Today: C, Go, Python, Java, Kotlin. To add a new language:

1. Append a per-language section to every rule's SKILL.md (or a `references/<lang>.md` file if that rule already exceeds 200 lines).
2. Update `pow10-overview` SKILL.md "Languages Covered" line.
3. Update README.
4. Triple-author across all three plugin directories.

## Citations

Rule wording paraphrases Holzmann (2006) and the JPL Institutional Coding Standard. Don't quote either verbatim at length — paraphrase, then cite.
