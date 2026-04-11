"""`pow10 explain N` implementation.

Reads the bundled rule data at plugin/data/rules/c/rule-NN.json, loads it via
`pow10.rules.load_rule`, and prints a human-readable summary. Runs entirely
off the generated data dir — not the source core/ dir — so the plugin works
when installed somewhere that has no `core/` checked out.

Data-dir resolution: plugin/pow10/explain.py -> parents[1] is plugin/, then
data/rules/c/rule-NN.json. This mirrors how plugin/pow10/rules.py resolves
its schema path.
"""

import sys
from pathlib import Path
from typing import List, TextIO

from pow10.rules import Rule, load_rule

# plugin/pow10/explain.py -> plugin/ is parents[1]
_PLUGIN_ROOT = Path(__file__).resolve().parents[1]
_DATA_RULES_C_DIR = _PLUGIN_ROOT / "data" / "rules" / "c"

MIN_RULE = 1
MAX_RULE = 10


class ExplainError(ValueError):
    """Raised when `explain` gets a bad argument."""


def _rule_path(number: int) -> Path:
    return _DATA_RULES_C_DIR / f"rule-{number:02d}.json"


def _load_rule_by_number(number: int) -> Rule:
    if not (MIN_RULE <= number <= MAX_RULE):
        raise ExplainError(
            f"rule {number} out of range; must be between {MIN_RULE} and {MAX_RULE}"
        )
    path = _rule_path(number)
    if not path.exists():
        raise ExplainError(
            f"rule data file not found: {path}. "
            "Run `python3 tools/generate.py` to regenerate plugin/data/."
        )
    return load_rule(path)


def _format_rule(rule: Rule) -> str:
    lines: List[str] = []
    lines.append(f"Rule {rule.number}: {rule.name}")
    lines.append(f"Severity: {rule.severity}")
    lines.append(f"Languages: {', '.join(rule.languages)}")
    lines.append("")
    lines.append("Rationale")
    lines.append("---------")
    lines.append(rule.rationale)
    lines.append("")
    lines.append("Enforcement")
    lines.append("-----------")
    lines.append(f"Strategy: {rule.enforcement.strategy}")
    if rule.enforcement.tools:
        lines.append(f"Tools:    {', '.join(rule.enforcement.tools)}")
    lines.append("")
    lines.append(rule.enforcement.notes)
    lines.append("")
    lines.append("Citations")
    lines.append("---------")
    for citation in rule.citations:
        lines.append(f"- {citation.source}: {citation.reference}")
    return "\n".join(lines) + "\n"


def explain(number: int, stream: TextIO = sys.stdout) -> int:
    """Print Rule <number>. Returns shell exit code (0 = success)."""
    rule = _load_rule_by_number(number)
    stream.write(_format_rule(rule))
    return 0
