# Rule 3 - No Dynamic Memory After Init (Python)

**Statement (Holzmann):** After the initialization phase, no heap allocation. All memory comes from fixed-size pools, the stack, or static buffers. Worst-case memory usage must be analyzable at build time.

**Profile (adapted):** applies in spirit; severity **advisory**.

CPython allocates on nearly every statement, so the literal rule is inapplicable. The real hazard for normal application code: unbounded, unvalidated external input driving unbounded memory growth in a long-running process, and materializing huge intermediates in hot loops when a streaming alternative exists.

## Checklist
- Cap any accumulator (bytes/list/dict) grown from unvalidated external input (upload body, paginated response, queue message)
- Bound long-lived in-memory caches with functools.lru_cache(maxsize=...) or an explicit eviction policy, never an unbounded dict
- Use generators/iterators instead of list comprehensions that materialize an entire dataset when the source is itself a stream
- Reuse pre-allocated NumPy buffers (np.empty + out=) in hot numeric loops instead of allocating fresh arrays per call
- Back allocation-removal claims with tracemalloc or memory_profiler measurements, not code reading
- Do not apply this rule to ordinary request/response/ORM-row code paths

## Violation

```python
def handle_upload(chunks):
    data = b""
    for chunk in chunks:  # attacker-controlled stream, no bound
        data += chunk
    return process(data)
```

## Fix

```python
MAX_BYTES = 10 * 1024 * 1024


def handle_upload(chunks):
    buf = bytearray()
    for chunk in chunks:
        buf += chunk
        if len(buf) > MAX_BYTES:
            raise ValueError("upload too large")
    return process(bytes(buf))
```

## Tooling
- `tracemalloc`: stdlib snapshot API - proxy: measures actual allocation growth to confirm a fix worked
- `memory_profiler`: pip package - proxy: line-by-line allocation profiling for hot loops
- `functools.lru_cache`: stdlib decorator - bounds a cache with `maxsize` instead of letting a dict grow unbounded
- `manual review`: no dedicated ruff or pylint rule enforces this - check accumulator loops and cache sites by hand

## Strict profile
Every unbounded container growth and every allocation inside a hot loop is a **[blocker]**, not advisory. Each external-input ingestion point needs a documented upper bound (constant or config value).
