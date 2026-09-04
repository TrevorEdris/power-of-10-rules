# Verified tool-name lists

Snapshot taken 2026-09-04 on macOS; used by `tools/validate.py` to reject citations of checks that do not exist.

| File | Source | Version |
| --- | --- | --- |
| golangci-linters.txt | `golangci-lint help linters` | version 2.8.0 |
| staticcheck-checks.txt | `staticcheck -list-checks` | staticcheck 2025.1.1 (0.6.1) |
| ruff-rules.txt | `ruff rule --all --output-format json` (removed rules excluded) | ruff 0.16.6 |
| pylint-msgs.txt | `pylint --list-msgs` | pylint 4.0.8 |
| clang-tidy-checks.txt | <https://clang.llvm.org/extra/clang-tidy/checks/list.html> | trunk docs |
| cppcheck-ids.txt | error ids scraped from cppcheck `lib/check*.cpp` on GitHub main (partial) | main |

Regenerate with newer tool versions when a citation is added that the lists reject.
