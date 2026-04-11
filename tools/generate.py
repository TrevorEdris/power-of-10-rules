#!/usr/bin/env python3
"""Generator entry point.

Reads core/rules/**/*.json, loads each rule via pow10.rules.load_rule, then
dispatches to per-target renderers that return strings. This module is the
only place that writes files — renderers are pure.

M2 targets (Claude Code plugin only):
  plugin/data/rules/c/rule-*.json   — copied verbatim from core/
  plugin/skills/rule-NN-<slug>/SKILL.md — 10 per-rule skills
  plugin/skills/<meta>/SKILL.md          — 7 meta skills
  plugin/agents/pow10-auditor.md         — subagent skeleton

Cursor + Codex adapters land in M6 / M7 respectively.

Deterministic + idempotent. CI runs this then `git diff --exit-code` via
tools/verify_no_drift.py.
"""

import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN_ROOT = REPO_ROOT / "plugin"
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

# Import order matters: PLUGIN_ROOT must be on sys.path before `pow10` imports.
from pow10.rules import load_rule  # noqa: E402

# tools/ is not on sys.path automatically; add REPO_ROOT so `tools.generate.*`
# renderer modules import cleanly.
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.generate.claude_code import (  # noqa: E402
    META_SKILLS,
    RULE_SLUGS,
    render_meta_skill,
    render_rule_skill,
    render_subagent,
)

# Output tree under plugin/. Everything under these paths is managed by the
# generator — if you edit by hand, verify_no_drift.py will fail.
PLUGIN_SKILLS_DIR = PLUGIN_ROOT / "skills"
PLUGIN_AGENTS_DIR = PLUGIN_ROOT / "agents"
PLUGIN_DATA_RULES_C_DIR = PLUGIN_ROOT / "data" / "rules" / "c"


def _write(path: Path, content: str) -> None:
    """Write content to path, creating parent dirs. Idempotent."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _reset_dir(path: Path, keep: tuple = (".gitkeep",)) -> None:
    """Remove all generated children of `path`, keeping only files in `keep`.

    We remove before writing so renamed / deleted inputs do not leave stale
    files behind. `.gitkeep` sentinels from M0 are preserved so empty
    directories still commit cleanly.
    """
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        return
    for child in sorted(path.iterdir()):
        if child.name in keep:
            continue
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()


def _load_all_c_rules() -> list:
    """Load every core/rules/c/rule-*.json into Rule dataclasses, sorted by number."""
    core_dir = REPO_ROOT / "core" / "rules" / "c"
    paths = sorted(core_dir.glob("rule-*.json"))
    rules = [load_rule(p) for p in paths]
    rules.sort(key=lambda r: r.number)
    return rules


def _emit_data_rules(rules: list) -> int:
    """Copy core/rules/c/*.json into plugin/data/rules/c/ verbatim.

    Deterministic: re-reads the JSON and re-writes it sorted + 2-space indented
    so small formatting differences in core/ do not flow through as drift.
    """
    # Full reset — mirrors skills/ and agents/ handling so orphaned files
    # (renamed slugs, hand-added suffixed copies) cannot survive regeneration.
    _reset_dir(PLUGIN_DATA_RULES_C_DIR)
    core_dir = REPO_ROOT / "core" / "rules" / "c"
    count = 0
    for path in sorted(core_dir.glob("rule-*.json")):
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        out_path = PLUGIN_DATA_RULES_C_DIR / path.name
        out_path.write_text(
            json.dumps(data, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        count += 1
    return count


def _emit_rule_skills(rules: list) -> int:
    """Write one plugin/skills/rule-NN-<slug>/SKILL.md per rule.

    Parent dir wipe is handled by `_reset_dir(PLUGIN_SKILLS_DIR)` in main().
    """
    count = 0
    for rule in rules:
        slug = RULE_SLUGS[rule.number]
        skill_path = PLUGIN_SKILLS_DIR / f"rule-{rule.number:02d}-{slug}" / "SKILL.md"
        _write(skill_path, render_rule_skill(rule))
        count += 1
    return count


def _emit_meta_skills() -> int:
    """Write one plugin/skills/<name>/SKILL.md per meta skill."""
    count = 0
    for name in sorted(META_SKILLS.keys()):
        skill_path = PLUGIN_SKILLS_DIR / name / "SKILL.md"
        _write(skill_path, render_meta_skill(name))
        count += 1
    return count


def _emit_subagent() -> None:
    agent_path = PLUGIN_AGENTS_DIR / "pow10-auditor.md"
    _write(agent_path, render_subagent())


def main() -> int:
    # Wipe the generated subtrees first so removed rules / renamed slugs do
    # not leave orphans. .gitkeep files are preserved.
    _reset_dir(PLUGIN_SKILLS_DIR)
    _reset_dir(PLUGIN_AGENTS_DIR)

    rules = _load_all_c_rules()
    if not rules:
        sys.stdout.write("generate: no rules found under core/rules/c/\n")
        return 0

    data_count = _emit_data_rules(rules)
    rule_skill_count = _emit_rule_skills(rules)
    meta_count = _emit_meta_skills()
    _emit_subagent()

    sys.stdout.write(
        "generate: wrote "
        f"{data_count} data file(s), "
        f"{rule_skill_count} rule skill(s), "
        f"{meta_count} meta skill(s), "
        "1 subagent\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
