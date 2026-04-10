"""M0 smoke tests — verify the bundled package is importable and the CLI dispatches.

These tests guard the two non-negotiables of the M0 scaffold:
  1. `import pow10` works from the bundled plugin/ directory (no pip install).
  2. `python3 -m pow10 version` exits 0 and prints the version.

If either fails, the zero-dep bundled-runtime design is broken.
"""

import subprocess
import sys
import unittest
from pathlib import Path

from tests import conftest  # noqa: F401  — sys.path setup

REPO_ROOT = Path(__file__).resolve().parents[2]
PLUGIN_ROOT = REPO_ROOT / "plugin"


class TestPackageImport(unittest.TestCase):
    def test_pow10_importable(self) -> None:
        import pow10

        self.assertTrue(hasattr(pow10, "__version__"))
        self.assertRegex(pow10.__version__, r"^\d+\.\d+\.\d+$")

    def test_cli_module_importable(self) -> None:
        from pow10.cli import main

        self.assertTrue(callable(main))


class TestCliVersion(unittest.TestCase):
    def test_version_subcommand_exits_zero(self) -> None:
        env_path = str(PLUGIN_ROOT)
        result = subprocess.run(
            [sys.executable, "-m", "pow10", "version"],
            cwd=REPO_ROOT,
            env={"PYTHONPATH": env_path, "PATH": "/usr/bin:/bin"},
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("pow10", result.stdout)

    def test_version_default_subcommand(self) -> None:
        env_path = str(PLUGIN_ROOT)
        result = subprocess.run(
            [sys.executable, "-m", "pow10"],
            cwd=REPO_ROOT,
            env={"PYTHONPATH": env_path, "PATH": "/usr/bin:/bin"},
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("pow10", result.stdout)


class TestPendingSubcommandStubs(unittest.TestCase):
    """M0 ships stubs for audit/report/list-waivers so bin wrappers exit 0.

    Real implementations land in M3. These tests guard the promise that the
    bundled bin wrappers do not crash on a fresh install.
    """

    def _run(self, subcommand: str) -> "subprocess.CompletedProcess[str]":
        env_path = str(PLUGIN_ROOT)
        return subprocess.run(
            [sys.executable, "-m", "pow10", subcommand],
            cwd=REPO_ROOT,
            env={"PYTHONPATH": env_path, "PATH": "/usr/bin:/bin"},
            capture_output=True,
            text=True,
        )

    def test_audit_stub_exits_zero(self) -> None:
        result = self._run("audit")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("not yet implemented", result.stdout)
        self.assertIn("M3", result.stdout)

    def test_report_stub_exits_zero(self) -> None:
        result = self._run("report")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("not yet implemented", result.stdout)

    def test_list_waivers_stub_exits_zero(self) -> None:
        result = self._run("list-waivers")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("not yet implemented", result.stdout)


class TestPythonVersionGate(unittest.TestCase):
    def test_runtime_python_is_supported(self) -> None:
        self.assertGreaterEqual(sys.version_info[:2], (3, 9))


if __name__ == "__main__":
    unittest.main()
