"""M2 tests for `pow10 explain N`.

The M2 exit criterion: `pow10 explain 2` returns correct content for Rule 2.
Also covers error paths: bad rule number, missing argument.

These tests run the CLI as a subprocess against the bundled plugin tree so
they exercise the same `sys.path` dance the bin wrappers do.
"""

import os
import subprocess
import sys
import unittest
from pathlib import Path

from tests import conftest  # noqa: F401 — sys.path setup

REPO_ROOT = Path(__file__).resolve().parents[2]
PLUGIN_ROOT = REPO_ROOT / "plugin"


def _run_cli(*args: str) -> "subprocess.CompletedProcess[str]":
    # Merge into the inherited env instead of replacing it. A scrubbed env
    # drops HOME / LANG / LC_* / PATH entries required by some macOS Python
    # builds (Homebrew, framework builds outside /usr/bin), and can produce
    # UTF-8 locale warnings or crashes on stdout writes.
    env = {**os.environ, "PYTHONPATH": str(PLUGIN_ROOT)}
    return subprocess.run(
        [sys.executable, "-m", "pow10", *args],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
    )


class TestExplainHappyPath(unittest.TestCase):
    def test_explain_rule_2_prints_rule_name_and_rationale(self) -> None:
        """M2 exit criterion. Output must contain Rule 2's name and rationale."""
        result = _run_cli("explain", "2")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("Rule 2", result.stdout)
        self.assertIn("loop", result.stdout.lower())
        self.assertIn("blocker", result.stdout)
        self.assertIn("Holzmann", result.stdout)

    def test_explain_rule_1_prints_control_flow_rule(self) -> None:
        result = _run_cli("explain", "1")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("Rule 1", result.stdout)
        self.assertIn("control flow", result.stdout.lower())

    def test_explain_every_rule_exits_zero(self) -> None:
        for n in range(1, 11):
            with self.subTest(rule=n):
                result = _run_cli("explain", str(n))
                self.assertEqual(
                    result.returncode, 0, msg=f"rule {n} failed: {result.stderr}"
                )
                self.assertIn(f"Rule {n}", result.stdout)


class TestExplainErrorPaths(unittest.TestCase):
    def test_explain_without_arg_errors(self) -> None:
        result = _run_cli("explain")
        self.assertNotEqual(result.returncode, 0)

    def test_explain_zero_is_rejected(self) -> None:
        result = _run_cli("explain", "0")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("1", result.stderr + result.stdout)
        self.assertIn("10", result.stderr + result.stdout)

    def test_explain_eleven_is_rejected(self) -> None:
        result = _run_cli("explain", "11")
        self.assertNotEqual(result.returncode, 0)

    def test_explain_non_integer_is_rejected(self) -> None:
        result = _run_cli("explain", "banana")
        self.assertNotEqual(result.returncode, 0)


class TestExplainBinWrapper(unittest.TestCase):
    """The pow10-explain bin wrapper must dispatch to the explain subcommand."""

    def test_bin_wrapper_prints_rule_content(self) -> None:
        wrapper = PLUGIN_ROOT / "bin" / "pow10-explain"
        self.assertTrue(wrapper.exists(), msg=f"missing {wrapper}")
        result = subprocess.run(
            [sys.executable, str(wrapper), "3"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("Rule 3", result.stdout)


if __name__ == "__main__":
    unittest.main()
