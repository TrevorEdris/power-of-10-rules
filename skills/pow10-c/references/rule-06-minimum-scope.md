# Rule 6 — C

## Forbidden

Mutable globals. Mutable file-scope `static` shared across functions. Variables declared at function top but used in only one branch. Function-top declarations forced by C89 — use C99 mid-block declarations.

## Violating example

```c
static int counter = 0;

void tick(void) {
    counter += 1;
}

int read_counter(void) {
    return counter;
}
```

`counter` is mutable file-scope state. Two functions implicitly coupled via shared mutation; not thread-safe; hidden from the call site.

## Remediation

Encapsulate in a struct passed explicitly:

```c
typedef struct {
    int value;
} ticker_t;

void ticker_init(ticker_t *t) {
    assert(t != NULL);
    t->value = 0;
}

void ticker_tick(ticker_t *t) {
    assert(t != NULL);
    t->value += 1;
}

int ticker_read(const ticker_t *t) {
    assert(t != NULL);
    return t->value;
}
```

Ownership is explicit; multiple instances are independent; testable in isolation.

## Hard checks

- `clang-tidy`:
  - `cppcoreguidelines-avoid-non-const-global-variables`
  - `readability-isolate-declaration`
- `cppcheck` `--enable=style` for non-const globals
