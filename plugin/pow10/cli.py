"""argparse dispatcher for pow10 subcommands.

Subcommands are wired up in later milestones:
  M3: audit
  M3: report
  M3: list-waivers
  M3: waive
  M2: explain
  M0: version (implemented here as a smoke test)
"""

import argparse
import sys
from typing import List, Optional

from pow10 import __version__


def _python_version_ok() -> bool:
    return sys.version_info >= (3, 9)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pow10",
        description="NASA Power of 10 rules runtime.",
    )
    parser.add_argument("--version", action="version", version=f"pow10 {__version__}")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("version", help="print pow10 version and exit")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    if not _python_version_ok():
        sys.stderr.write(
            "pow10 requires Python 3.9 or later. "
            "On macOS: xcode-select --install\n"
        )
        return 2
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "version" or args.command is None:
        sys.stdout.write(f"pow10 {__version__}\n")
        return 0
    parser.error(f"unknown command: {args.command}")
    return 1
