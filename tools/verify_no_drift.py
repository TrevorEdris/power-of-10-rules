#!/usr/bin/env python3
"""CI drift check.

Runs tools/generate.py, then `git diff --exit-code` across the generated
output directories. Non-zero exit = someone edited generated files by hand
or forgot to regenerate after editing core/.

Populated in M2. M0 ships a no-op stub that CI can invoke safely.
"""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GENERATED_PATHS = [
    "plugin/skills",
    "plugin/data",
    "plugin/agents",
    "cursor/.cursor",
    "codex",
    ".claude-plugin/marketplace.json",
]


def main() -> int:
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "tools" / "generate.py")],
        cwd=REPO_ROOT,
    )
    if result.returncode != 0:
        return result.returncode
    diff = subprocess.run(
        ["git", "diff", "--exit-code", "--", *GENERATED_PATHS],
        cwd=REPO_ROOT,
    )
    return diff.returncode


if __name__ == "__main__":
    sys.exit(main())
