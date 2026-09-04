# Rule 3 — C

## Forbidden

`malloc`, `calloc`, `realloc`, `free`, `alloca` after the init phase. Init phase ends at the `// pow10:init-end` marker.

## Violating example

```c
void handle_packet(size_t n) {
    char *buf = malloc(n);
    read_packet(buf, n);
    process_packet(buf, n);
    free(buf);
}
```

Heap call on every packet. Failure mode (allocation returns NULL) is not analyzable; fragmentation grows over mission lifetime.

## Remediation

Use a fixed static buffer with a size-check assertion:

```c
#define BUF_MAX 2048

void handle_packet(size_t n) {
    static char buf[BUF_MAX];
    assert(n <= BUF_MAX);
    read_packet(buf, n);
    process_packet(buf, n);
}
```

Worst-case memory now `BUF_MAX` bytes, known at link time. Oversize input fails fast via the assertion (Rule 5).

## Hard checks

- `clang-tidy`: `cppcoreguidelines-no-malloc`
- `cppcheck` for any `malloc`/`free`/`alloca` outside init
- Manual review of init-end marker placement
