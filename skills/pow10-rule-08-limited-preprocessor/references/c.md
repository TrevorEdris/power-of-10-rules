# Rule 8 — C

## Allowed

`#include`, `#define CONST 42` (object-like simple constants), narrow `#ifdef PLATFORM_X` for platform differences.

## Forbidden

Token pasting (`##`), stringification (`#`), recursive/variadic macros, function-like macros with side-effect risk, `#ifdef` that varies function signatures across files.

## Violating example

```c
#define SQUARE(x) ((x) * (x))

int n = SQUARE(i++);
```

`i` is incremented twice — undefined behavior. The macro's expansion is invisible at the call site; the bug looks like a normal function call.

## Remediation

Replace with a `static inline` function:

```c
static inline int square(int x) {
    return x * x;
}

int n = square(i++);
```

Single evaluation of `i++`. Type-checked. Steppable in the debugger.

## Hard checks

- `clang-tidy`:
  - `cppcoreguidelines-macro-usage`
  - `bugprone-macro-parentheses`
  - `bugprone-reserved-identifier`
- `cppcheck` `--enable=style` for macro pitfalls
