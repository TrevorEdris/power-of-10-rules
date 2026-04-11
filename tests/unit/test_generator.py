"""M2 tests for the generator pipeline.

Covers:
  - tools/generate/claude_code.py renderers (pure string in/out)
  - tools/generate.py end-to-end: rendered files land in expected tree
  - Slug table correctness (one slug per rule, 1..10)

Structural tests only — no snapshot-style content pinning. If a heading
changes, tests still pass; only missing files or missing required fields
break the build.
"""

import json
import subprocess
import sys
import unittest
from pathlib import Path

from tests import conftest  # noqa: F401 — sys.path setup

REPO_ROOT = Path(__file__).resolve().parents[2]
PLUGIN_ROOT = REPO_ROOT / "plugin"


class TestRuleSlugs(unittest.TestCase):
    def test_slug_table_covers_all_ten_rules(self) -> None:
        from tools.generate.claude_code import RULE_SLUGS

        self.assertEqual(set(RULE_SLUGS.keys()), set(range(1, 11)))
        for number, slug in RULE_SLUGS.items():
            self.assertRegex(
                slug,
                r"^[a-z][a-z0-9-]*[a-z0-9]$",
                msg=f"rule {number} slug {slug!r} must be kebab-case",
            )

    def test_slugs_are_unique(self) -> None:
        from tools.generate.claude_code import RULE_SLUGS

        self.assertEqual(len(set(RULE_SLUGS.values())), 10)


class TestRenderRuleSkill(unittest.TestCase):
    """render_rule_skill takes a Rule dataclass and returns a SKILL.md string."""

    def _load_rule(self, number: int):
        from pow10.rules import load_rule

        path = REPO_ROOT / "core" / "rules" / "c" / f"rule-{number:02d}.json"
        return load_rule(path)

    def test_contains_yaml_frontmatter(self) -> None:
        from tools.generate.claude_code import render_rule_skill

        rule = self._load_rule(1)
        rendered = render_rule_skill(rule)
        self.assertTrue(rendered.startswith("---\n"), msg=rendered[:80])
        self.assertIn("\n---\n", rendered[4:])

    def test_frontmatter_has_name_and_description(self) -> None:
        from tools.generate.claude_code import render_rule_skill

        rule = self._load_rule(1)
        rendered = render_rule_skill(rule)
        frontmatter = rendered.split("---\n")[1]
        self.assertIn("name:", frontmatter)
        self.assertIn("description:", frontmatter)

    def test_body_includes_rule_name_and_rationale(self) -> None:
        from tools.generate.claude_code import render_rule_skill

        rule = self._load_rule(1)
        rendered = render_rule_skill(rule)
        self.assertIn(rule.name, rendered)
        self.assertIn(rule.rationale, rendered)

    def test_body_includes_citations(self) -> None:
        from tools.generate.claude_code import render_rule_skill

        rule = self._load_rule(1)
        rendered = render_rule_skill(rule)
        self.assertIn("Holzmann 2006", rendered)

    def test_body_includes_enforcement_notes(self) -> None:
        from tools.generate.claude_code import render_rule_skill

        rule = self._load_rule(1)
        rendered = render_rule_skill(rule)
        self.assertIn(rule.enforcement.notes, rendered)


class TestRenderMetaSkill(unittest.TestCase):
    def test_known_meta_skills(self) -> None:
        from tools.generate.claude_code import META_SKILLS

        expected = {"audit", "fix", "onboard", "report", "waive", "list-waivers", "explain"}
        self.assertEqual(set(META_SKILLS.keys()), expected)

    def test_render_meta_skill_has_frontmatter(self) -> None:
        from tools.generate.claude_code import render_meta_skill

        rendered = render_meta_skill("explain")
        self.assertTrue(rendered.startswith("---\n"))
        self.assertIn("name:", rendered)
        self.assertIn("description:", rendered)


class TestRenderSubagent(unittest.TestCase):
    def test_subagent_has_frontmatter_and_audit_reference(self) -> None:
        from tools.generate.claude_code import render_subagent

        rendered = render_subagent()
        self.assertTrue(rendered.startswith("---\n"))
        self.assertIn("name: pow10-auditor", rendered)
        # M2 ships skeleton; real audit logic lands in M3.
        self.assertIn("pow10 audit", rendered)


class TestGenerateMainWritesTree(unittest.TestCase):
    """Run tools/generate.py and assert the expected files land on disk.

    Uses the real repo tree (tools/generate.py writes into REPO_ROOT). After
    running, we only check for presence + required keys — content diffs live
    in the snapshot-free world chosen in M2 design decision #5.
    """

    def setUp(self) -> None:
        result = subprocess.run(
            [sys.executable, "tools/generate.py"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)

    def test_data_rules_c_directory_populated(self) -> None:
        data_dir = REPO_ROOT / "plugin" / "data" / "rules" / "c"
        files = sorted(data_dir.glob("rule-*.json"))
        self.assertEqual(len(files), 10, msg=[f.name for f in files])
        # Every emitted data file must match the core source verbatim.
        for data_path in files:
            core_path = REPO_ROOT / "core" / "rules" / "c" / data_path.name
            self.assertEqual(
                json.loads(data_path.read_text(encoding="utf-8")),
                json.loads(core_path.read_text(encoding="utf-8")),
                msg=f"{data_path.name} drifted from core",
            )

    def test_rule_skill_dirs_exist(self) -> None:
        from tools.generate.claude_code import RULE_SLUGS

        skills_dir = REPO_ROOT / "plugin" / "skills"
        for number, slug in RULE_SLUGS.items():
            skill_dir = skills_dir / f"rule-{number:02d}-{slug}"
            skill_md = skill_dir / "SKILL.md"
            self.assertTrue(skill_md.exists(), msg=f"missing {skill_md}")
            content = skill_md.read_text(encoding="utf-8")
            self.assertTrue(content.startswith("---\n"))
            self.assertIn("name:", content)

    def test_meta_skill_dirs_exist(self) -> None:
        skills_dir = REPO_ROOT / "plugin" / "skills"
        for name in ("audit", "fix", "onboard", "report", "waive", "list-waivers", "explain"):
            skill_md = skills_dir / name / "SKILL.md"
            self.assertTrue(skill_md.exists(), msg=f"missing {skill_md}")

    def test_subagent_exists(self) -> None:
        agent_path = REPO_ROOT / "plugin" / "agents" / "pow10-auditor.md"
        self.assertTrue(agent_path.exists())
        content = agent_path.read_text(encoding="utf-8")
        self.assertIn("pow10-auditor", content)

    def test_generator_is_idempotent(self) -> None:
        """Running generate.py twice produces byte-identical output."""
        first = (REPO_ROOT / "plugin" / "skills" / "explain" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        result = subprocess.run(
            [sys.executable, "tools/generate.py"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        second = (REPO_ROOT / "plugin" / "skills" / "explain" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
