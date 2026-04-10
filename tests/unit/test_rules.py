"""M1 tests for the Rule dataclass, loader, and validator.

These tests cover the core schema layer: constructing Rule/Citation/Enforcement
dataclasses, loading a rule from a JSON file, and validating raw dict input
against the hand-written schema at core/rules/schema.json.
"""

import json
import tempfile
import unittest
from pathlib import Path

from tests import conftest  # noqa: F401 — sys.path setup


VALID_RULE_DICT = {
    "id": "pow10-1",
    "number": 1,
    "name": "Restrict control flow to simple constructs",
    "rationale": "Simpler control flow is easier to verify statically and by inspection.",
    "severity": "blocker",
    "languages": ["c"],
    "enforcement": {
        "strategy": "static-analysis",
        "tools": ["clang-tidy"],
        "notes": "Forbid goto, setjmp, longjmp, recursion.",
    },
    "citations": [
        {
            "source": "Holzmann 2006",
            "reference": "The Power of 10: Rules for Developing Safety-Critical Code, IEEE Computer 39(6), 95-97",
        }
    ],
}


class TestRuleDataclass(unittest.TestCase):
    def test_construct_from_valid_fields(self) -> None:
        from pow10.rules import Citation, Enforcement, Rule

        rule = Rule(
            id="pow10-1",
            number=1,
            name="Restrict control flow",
            rationale="why",
            severity="blocker",
            languages=("c",),
            enforcement=Enforcement(
                strategy="static-analysis",
                tools=("clang-tidy",),
                notes="n",
            ),
            citations=(Citation(source="Holzmann 2006", reference="IEEE Computer 39(6)"),),
        )
        self.assertEqual(rule.id, "pow10-1")
        self.assertEqual(rule.number, 1)
        self.assertEqual(rule.languages, ("c",))
        self.assertEqual(rule.enforcement.strategy, "static-analysis")
        self.assertEqual(rule.citations[0].source, "Holzmann 2006")

    def test_rule_is_frozen(self) -> None:
        """Rules are immutable once loaded — callers must not mutate shared state."""
        from dataclasses import FrozenInstanceError

        from pow10.rules import Citation, Enforcement, Rule

        rule = Rule(
            id="pow10-1",
            number=1,
            name="n",
            rationale="r",
            severity="blocker",
            languages=("c",),
            enforcement=Enforcement(strategy="static-analysis", tools=(), notes="n"),
            citations=(Citation(source="s", reference="r"),),
        )
        with self.assertRaises(FrozenInstanceError):
            rule.id = "pow10-2"  # type: ignore[misc]


class TestLoadRule(unittest.TestCase):
    def test_load_valid_rule_from_file(self) -> None:
        from pow10.rules import load_rule

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(VALID_RULE_DICT, f)
            tmp_path = Path(f.name)
        try:
            rule = load_rule(tmp_path)
            self.assertEqual(rule.id, "pow10-1")
            self.assertEqual(rule.number, 1)
            self.assertEqual(rule.languages, ("c",))
            self.assertEqual(rule.enforcement.tools, ("clang-tidy",))
            self.assertEqual(len(rule.citations), 1)
        finally:
            tmp_path.unlink()

    def test_load_rule_raises_on_missing_file(self) -> None:
        from pow10.rules import load_rule

        with self.assertRaises(FileNotFoundError):
            load_rule(Path("/nonexistent/rule.json"))


class TestValidateRule(unittest.TestCase):
    def test_valid_rule_returns_no_errors(self) -> None:
        from pow10.rules import validate_rule

        errors = validate_rule(VALID_RULE_DICT)
        self.assertEqual(errors, [], msg=f"expected no errors, got {errors}")

    def test_missing_id_is_reported(self) -> None:
        from pow10.rules import validate_rule

        data = dict(VALID_RULE_DICT)
        del data["id"]
        errors = validate_rule(data)
        self.assertTrue(any("id" in e for e in errors), msg=errors)

    def test_bad_severity_enum_is_reported(self) -> None:
        from pow10.rules import validate_rule

        data = dict(VALID_RULE_DICT)
        data["severity"] = "catastrophic"
        errors = validate_rule(data)
        self.assertTrue(any("severity" in e for e in errors), msg=errors)

    def test_unknown_property_is_reported(self) -> None:
        from pow10.rules import validate_rule

        data = dict(VALID_RULE_DICT)
        data["extraneous"] = "nope"
        errors = validate_rule(data)
        self.assertTrue(any("extraneous" in e for e in errors), msg=errors)

    def test_bad_id_pattern_is_reported(self) -> None:
        from pow10.rules import validate_rule

        data = dict(VALID_RULE_DICT)
        data["id"] = "nasa-1"
        errors = validate_rule(data)
        self.assertTrue(any("id" in e for e in errors), msg=errors)

    def test_non_object_input_is_reported(self) -> None:
        from pow10.rules import validate_rule

        errors = validate_rule(["not", "an", "object"])  # type: ignore[arg-type]
        self.assertTrue(len(errors) >= 1)

    def test_id_with_trailing_newline_is_rejected(self) -> None:
        """Python's re.match+`$` would accept a trailing newline. ECMA 262 (the
        regex flavor JSON Schema draft-7 specifies) would not. Validator must
        use re.fullmatch so the stdlib implementation matches the spec."""
        from pow10.rules import validate_rule

        data = dict(VALID_RULE_DICT)
        data["id"] = "pow10-1\n"
        errors = validate_rule(data)
        self.assertTrue(
            any("id" in e and "pattern" in e for e in errors),
            msg=f"expected pattern error on id, got {errors}",
        )


class TestSchemaDriftGuard(unittest.TestCase):
    """The hand-rolled validator and hand-written schema must stay in sync.

    If someone adds a keyword like `minLength` to schema.json expecting it to
    be enforced, _assert_known_keywords must raise so the drift is loud.
    """

    def test_unsupported_keyword_in_schema_raises(self) -> None:
        from pow10.rules import SchemaDriftError, _assert_known_keywords

        drifted = {
            "type": "object",
            "properties": {
                "name": {"type": "string", "minLength": 5},
            },
        }
        with self.assertRaises(SchemaDriftError) as ctx:
            _assert_known_keywords(drifted, "$")
        self.assertIn("minLength", str(ctx.exception))

    def test_supported_keywords_do_not_raise(self) -> None:
        from pow10.rules import _assert_known_keywords, load_schema

        # The real schema.json must be clean — if it ever drifts, this fails.
        _assert_known_keywords(load_schema(), "$")


class TestLoadRuleValidationError(unittest.TestCase):
    def test_load_rule_raises_on_semantic_violation(self) -> None:
        """load_rule must surface validation failures as RuleValidationError,
        not let the KeyError escape from the downstream dataclass construction."""
        from pow10.rules import RuleValidationError, load_rule

        broken = dict(VALID_RULE_DICT)
        del broken["severity"]
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(broken, f)
            tmp_path = Path(f.name)
        try:
            with self.assertRaises(RuleValidationError) as ctx:
                load_rule(tmp_path)
            self.assertIn(str(tmp_path), str(ctx.exception))
            self.assertIn("severity", str(ctx.exception))
        finally:
            tmp_path.unlink()


class TestValidateCliEntrypoint(unittest.TestCase):
    """tools/validate.py is the entry point CI calls.

    Proves: exit 0 on clean repo, exit 1 with the bad path reported on broken rule,
    and that schema.json itself is skipped (it has no `id` field so would fail
    rule-shape validation if the walker didn't exclude it).
    """

    def test_validate_cli_exits_zero_on_clean_repo(self) -> None:
        import subprocess
        import sys

        repo_root = Path(__file__).resolve().parents[2]
        result = subprocess.run(
            [sys.executable, "tools/validate.py"],
            cwd=repo_root,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("OK", result.stdout)

    def test_validate_cli_exits_nonzero_on_broken_rule(self) -> None:
        import subprocess
        import sys

        repo_root = Path(__file__).resolve().parents[2]
        bad_rule = repo_root / "core" / "rules" / "c" / "rule-bad-test.json"
        bad_rule.write_text(json.dumps({"id": "not-valid"}), encoding="utf-8")
        self.addCleanup(lambda: bad_rule.unlink(missing_ok=True))
        result = subprocess.run(
            [sys.executable, "tools/validate.py"],
            cwd=repo_root,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("rule-bad-test.json", result.stderr)

    def test_validate_cli_reports_json_decode_error(self) -> None:
        """tools/validate.py has a documented JSONDecodeError branch; prove it.
        A malformed rule file should exit 1 with 'invalid JSON' in stderr."""
        import subprocess
        import sys

        repo_root = Path(__file__).resolve().parents[2]
        bad_rule = repo_root / "core" / "rules" / "c" / "rule-malformed.json"
        bad_rule.write_text("{not valid json", encoding="utf-8")
        self.addCleanup(lambda: bad_rule.unlink(missing_ok=True))
        result = subprocess.run(
            [sys.executable, "tools/validate.py"],
            cwd=repo_root,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("invalid JSON", result.stderr)
        self.assertIn("rule-malformed.json", result.stderr)


class TestLoadAllCRules(unittest.TestCase):
    """Golden test — every C rule on disk must load and validate."""

    def test_all_ten_c_rules_load_and_validate(self) -> None:
        from pow10.rules import load_rule, validate_rule

        repo_root = Path(__file__).resolve().parents[2]
        rules_dir = repo_root / "core" / "rules" / "c"
        rule_files = sorted(rules_dir.glob("rule-*.json"))
        self.assertEqual(
            len(rule_files),
            10,
            msg=f"expected 10 C rule files, found {len(rule_files)}: {rule_files}",
        )
        seen_numbers = set()
        for path in rule_files:
            with path.open(encoding="utf-8") as f:
                data = json.load(f)
            errors = validate_rule(data)
            self.assertEqual(errors, [], msg=f"{path.name}: {errors}")
            rule = load_rule(path)
            self.assertIn("c", rule.languages)
            seen_numbers.add(rule.number)
        self.assertEqual(seen_numbers, set(range(1, 11)))


if __name__ == "__main__":
    unittest.main()
