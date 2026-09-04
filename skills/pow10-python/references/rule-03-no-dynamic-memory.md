# Rule 3 — Python

## Forbidden in spirit

Cannot ban allocation in CPython — the runtime allocates constantly. Apply Rule 3 by pre-allocating buffers, avoiding list/dict comprehensions in hot loops, reusing arrays. For true safety-critical Python (rare), use MicroPython with bounded heap and zero GC pauses.

## Violating example

```python
def normalize(rows):
    return [[float(x) / 255.0 for x in row] for row in rows]
```

A new outer list, a new inner list per row, and a new float per cell. For a 1000×1000 frame, that's a million floats and a thousand lists allocated per call.

## Remediation

Reuse a pre-allocated NumPy array:

```python
import numpy as np

class Normalizer:
    def __init__(self, height: int, width: int) -> None:
        self._buf = np.empty((height, width), dtype=np.float32)

    def normalize(self, rows: np.ndarray) -> np.ndarray:
        np.divide(rows, 255.0, out=self._buf, casting="unsafe")
        return self._buf
```

`out=self._buf` writes in place; one buffer, reused indefinitely.

## Hard checks

- `tracemalloc` for allocation snapshots
- `memory_profiler` for line-by-line allocation
- `pytest-benchmark` with `--benchmark-allocs` (needs plugin)
