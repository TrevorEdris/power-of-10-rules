"""Shared test bootstrap.

Prepends the bundled plugin/ directory to sys.path so `import pow10` resolves
without installation. Imported by every test module via `from tests import conftest`.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN_ROOT = REPO_ROOT / "plugin"

if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))
