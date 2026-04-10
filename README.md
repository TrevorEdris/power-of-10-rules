# power-of-10-rules

NASA's [Power of 10 rules for developing safety-critical code][holzmann] as agentic skills for Claude Code, Cursor, and Codex.

One source of truth — rendered to three platforms. Zero runtime dependencies beyond Python 3.9 stdlib.

## Status

v0.0.1 — scaffolding (M0 Bootstrap). Rules logic lands in M1+.

## Install

### Claude Code (primary)

```bash
/plugin marketplace add TrevorEdris/power-of-10-rules
/plugin install pow10@pow10
/pow10:onboard
```

### Cursor

```bash
git clone https://github.com/TrevorEdris/power-of-10-rules /tmp/pow10
cp -r /tmp/pow10/cursor/.cursor/rules/* .cursor/rules/
```

### Codex

```bash
cp /tmp/pow10/codex/AGENTS.pow10.md ./
bash /tmp/pow10/codex/install.sh
```

## Requirements

- Python 3.9 or later on `PATH` (ships with macOS Command Line Tools)
- Per-language analyzer binaries on `PATH` (`clang-tidy`, `staticcheck`, `ruff`, `detekt`, `spotbugs`) — `pow10:onboard` verifies presence and reports install commands

## Design principles

1. **Single source of truth, three rendered targets.** Rule content lives once in `core/*.json`. A Python generator emits Claude Code plugin, Cursor rules, and Codex prompts from the same source. CI enforces no drift.
2. **Zero runtime dependencies.** Stdlib-only. No `pip install`, no `uv`, no PyPI.
3. **JSON everywhere for data.** Rules, language profiles, analyzer configs, and consumer config all use JSON.

## Development

```bash
git clone git@github.com:TrevorEdris/power-of-10-rules.git
cd power-of-10-rules
python3 -m unittest discover tests        # run tests
python3 tools/validate.py                  # validate core/*.json
python3 tools/generate.py                  # regenerate plugin/, cursor/, codex/
python3 tools/verify_no_drift.py           # fails if generated outputs drift from core/
```

No `pip install` step. `python3` on `PATH` is the only prerequisite.

## License

MIT. See [LICENSE](LICENSE).

Rule text cites Holzmann (2006) and the JPL Institutional Coding Standard; paraphrases used throughout.

[holzmann]: https://spinroot.com/gerard/pdf/P10.pdf
