# core/ — source of truth

Language/platform-neutral JSON definitions. Everything in `plugin/`, `cursor/`, and `codex/` is rendered from here by `python3 tools/generate.py`.

- `rules/` — 10 JSONs, one per Power of 10 rule (populated in M1)
- `languages/` — per-language profiles (c, go, python, kotlin, java — populated in M1 and M4)
- `analyzers/` — per-tool config (clang-tidy, staticcheck, ruff, detekt, spotbugs — populated in M1 and M5)
- `skills/` — skill metadata (audit, fix, onboard, report, waive, list-waivers, explain — populated in M2)

Do not edit generated output. Edit files here and run `python3 tools/generate.py`.
