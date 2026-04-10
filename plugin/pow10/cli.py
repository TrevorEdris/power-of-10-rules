"""argparse dispatcher for pow10 subcommands.

Subcommands wired up across milestones:
  M0: version          (implemented)
  M0: audit            (stub — lands in M3)
  M0: report           (stub — lands in M3)
  M0: list-waivers     (stub — lands in M3)
  M3: waive
  M2: explain

M0 ships stubs for audit/report/list-waivers so the bin wrappers exit 0 with a
"not yet implemented" message instead of crashing on an unknown subcommand.
"""

import argparse
import sys
from typing import List, Optional

from pow10 import __version__

# Subcommands stubbed in M0 and implemented in later milestones. Each entry
# maps the subcommand name to the milestone that will implement it.
_PENDING_SUBCOMMANDS = {
    "audit": "M3",
    "report": "M3",
    "list-waivers": "M3",
}


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
    for name, milestone in _PENDING_SUBCOMMANDS.items():
        sub.add_parser(name, help=f"not yet implemented (lands in {milestone})")
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
    if args.command in _PENDING_SUBCOMMANDS:
        milestone = _PENDING_SUBCOMMANDS[args.command]
        sys.stdout.write(
            f"pow10 {args.command}: not yet implemented (lands in {milestone})\n"
        )
        return 0
    # argparse rejects unknown commands during parse_args, so this is unreachable.
    parser.error(f"unknown command: {args.command}")
