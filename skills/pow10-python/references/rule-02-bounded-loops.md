# Rule 2 - Bounded Loops (Python)

**Statement (Holzmann):** Every loop must carry an explicit, statically verifiable upper bound on its iteration count, ideally a compile-time constant, or asserted against a fixed maximum when the bound depends on runtime input.

**Profile (adapted):** applies partially; severity **medium**.

The literal compile-time-constant bound does not fit long-lived Python services (a daemon's `while True` main loop is intentional and correct). The hazard that matters for app code is a loop that can spin forever waiting on something that may never happen - a poll, a retry, a queue drain - because it has no attempt cap or timeout. Long-lived process loops are fine when they check an explicit shutdown signal each pass; the concern is loops gated only on external state that may never arrive.

## Checklist
- Cap polling/`while True` loops with a max-iteration count or wall-clock timeout, and raise or log when the cap is hit.
- Bound retry logic with an explicit counter or a retry library's stop condition, not a bare `while` around a fallible call.
- Guard recursive tree/graph walks used in place of iteration with an explicit depth limit.
- Break out of loops over sockets, queues, or generators from external sources via a timeout, sentinel, or cancellation event.
- Check a shutdown flag or event each iteration in long-lived worker/daemon loops.

## Violation

```python
import time


def poll_status(job_id):
    while True:
        status = get_status(job_id)
        if status == "done":
            return status
        time.sleep(1)
```

## Fix

```python
import time


def poll_status(job_id, max_attempts=60, interval=1):
    for _ in range(max_attempts):
        status = get_status(job_id)
        if status == "done":
            return status
        time.sleep(interval)
    raise TimeoutError(f"job {job_id} did not finish in {max_attempts * interval}s")
```

## Tooling
- `manual review`: flag `while True` and unbounded `while cond` loops with no counter, timeout, or shutdown-event check; verify retry loops use a bounded-attempts pattern.

## Strict profile
Every loop must carry a static bound, `while True` included - severity **blocker**.
