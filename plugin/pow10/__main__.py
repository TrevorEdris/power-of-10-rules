"""Entry point: `python3 -m pow10 <subcommand>`."""

import sys

from pow10.cli import main

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
