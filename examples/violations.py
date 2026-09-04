"""Smoke-test fixture. Every function breaks at least one Power of 10 rule on purpose.

Expected findings (adapted profile): R1 depth, R2 wait_ready, R3 CACHE, R5 handle,
R6 bump, R7 load, R8 run. Strict adds R1 on any recursion and R9 on the callable table.
"""

import json
import subprocess
import time

CACHE: dict[str, bytes] = {}  # R3: grows for the process lifetime, never evicted
counter = 0


def depth(node: object, d: int = 0) -> int:
    """Walks arbitrarily nested input with no cap. R1."""
    if not isinstance(node, dict):
        return d
    return max((depth(v, d + 1) for v in node.values()), default=d)


def wait_ready(check) -> None:
    """Polls forever. R2."""
    while True:
        if check():
            return
        time.sleep(0.1)


def handle(payload: dict) -> str:
    """Validates request input with assert; vanishes under -O. R5."""
    assert "user" in payload, "user required"
    return payload["user"]


def bump() -> int:
    """Mutates a module global. R6."""
    global counter
    counter += 1
    return counter


def load(path: str) -> dict:
    """Swallows every error and ignores the return code. R7."""
    try:
        subprocess.run(["cat", path], capture_output=True)
        return json.loads(open(path).read())
    except Exception:
        return {}


def run(expr: str) -> object:
    """Evaluates a string from the caller. R8."""
    return eval(expr)


HANDLERS = {"depth": depth, "bump": bump, "run": run}  # R9 under strict: open callable table
