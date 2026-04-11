"""argparse dispatcher for pow10 subcommands.

Subcommands wired up across milestones:
  version         (M0, implemented)
  explain         (M2, implemented)
  audit           (M0 stub -> M3)
  fix             (M2 stub -> M3)
  onboard         (M2 stub -> M3)
  report          (M0 stub -> M3)
  waive           (M2 stub -> M3)
  list-waivers    (M0 stub -> M3)

Stub subcommands exit 0 with a "not yet implemented" message so bin wrappers
and Claude Code skill surfaces work end-to-end on a fresh install.
"""

import argparse
import sys
from typing import List, Optional

from pow10 import __version__
from pow10.explain import MAX_RULE, MIN_RULE, ExplainError, explain


def _rule_number(raw: str) -> int:
    """argparse type callable — unifies non-integer and out-of-range errors.

    Without this, `pow10 explain banana` exits via argparse (code 2, generic
    message) while `pow10 explain 11` exits via ExplainError (code 2, domain
    message). Routing both through one message makes the CLI UX consistent.
    """
    try:
        number = int(raw)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"rule must be an integer between {MIN_RULE} and {MAX_RULE}; got {raw!r}"
        )
    if not (MIN_RULE <= number <= MAX_RULE):
        raise argparse.ArgumentTypeError(
            f"rule {number} out of range; must be between {MIN_RULE} and {MAX_RULE}"
        )
    return number

# Subcommands stubbed out until their owning milestone lands. Each entry
# maps the subcommand name to the milestone that will implement it.
_PENDING_SUBCOMMANDS = {
    "audit": "M3",
    "fix": "M3",
    "onboard": "M3",
    "report": "M3",
    "waive": "M3",
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

    explain_parser = sub.add_parser(
        "explain",
        help="print the full text of a Power of 10 rule",
    )
    explain_parser.add_argument(
        "number",
        type=_rule_number,
        help=f"rule number ({MIN_RULE}-{MAX_RULE})",
    )

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
    if args.command == "explain":
        try:
            return explain(args.number)
        except ExplainError as err:
            sys.stderr.write(f"pow10 explain: {err}\n")
            return 2
    if args.command in _PENDING_SUBCOMMANDS:
        milestone = _PENDING_SUBCOMMANDS[args.command]
        sys.stdout.write(
            f"pow10 {args.command}: not yet implemented (lands in {milestone})\n"
        )
        return 0
    # argparse rejects unknown commands during parse_args, so this is unreachable.
    parser.error(f"unknown command: {args.command}")
