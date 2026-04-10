#!/usr/bin/env python3
"""Validator entry point.

Loads everything under core/ via pow10.rules.load_rule() and friends, runs
validate_rule() against each, and reports errors. Exit 0 = valid.

Populated in M1. M0 ships a no-op stub.
"""

import sys


def main() -> int:
    sys.stdout.write("validate: no-op (core/ is empty; populated in M1)\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
