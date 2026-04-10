#!/usr/bin/env python3
"""Validator entry point.

Walks core/rules/**/*.json, runs pow10.rules.validate_rule() against each file,
and reports errors. Exit 0 on clean validation; exit 1 on any validation
failure; exit 2 on unexpected error (missing schema, unreadable file).

The schema file itself (core/rules/schema.json) is skipped.
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN_ROOT = REPO_ROOT / "plugin"
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from pow10.rules import validate_rule  # noqa: E402


def _iter_rule_files(rules_dir: Path):
    """Yield every .json file under rules_dir except the schema itself."""
    for path in sorted(rules_dir.rglob("*.json")):
        if path.name == "schema.json":
            continue
        yield path


def main() -> int:
    rules_dir = REPO_ROOT / "core" / "rules"
    if not rules_dir.exists():
        sys.stderr.write(f"validate: {rules_dir} does not exist\n")
        return 2

    rule_files = list(_iter_rule_files(rules_dir))
    if not rule_files:
        sys.stdout.write("validate: no rule files found under core/rules/\n")
        return 0

    total_errors = 0
    for path in rule_files:
        rel = path.relative_to(REPO_ROOT)
        try:
            with path.open(encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            sys.stderr.write(f"validate: {rel}: invalid JSON: {e}\n")
            total_errors += 1
            continue

        errors = validate_rule(data)
        if errors:
            for err in errors:
                sys.stderr.write(f"validate: {rel}: {err}\n")
            total_errors += len(errors)

    if total_errors:
        sys.stderr.write(
            f"validate: {total_errors} error(s) across {len(rule_files)} file(s)\n"
        )
        return 1

    sys.stdout.write(f"validate: {len(rule_files)} rule file(s) OK\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
