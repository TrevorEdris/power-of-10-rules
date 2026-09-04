# Rule 8 - Limited Preprocessor (C)

**Statement (Holzmann):** restrict preprocessor use to header inclusion and simple macro definitions (object-like or simple function-like); forbid token pasting, stringification, variable-argument lists, and recursive macro calls, and flag every conditional-compilation directive beyond an include guard.

**Profile (literal):** applies fully; severity **high**.

The preprocessor runs before the compiler sees the source, so a macro's expansion is invisible at the call site - side effects, type mismatches, and multiple-evaluation bugs hide behind what looks like a normal function call. `#ifdef` beyond include guards forks the source tree into untested variants. The rule keeps every line the compiler and debugger actually check visible in the source.

## Checklist
- Allow only `#include` and object-like or simple function-like `#define` constants
- Forbid `##` token pasting and `#` stringification in any macro
- Forbid recursive macro expansion and variadic (`...`) macro argument lists
- Replace function-like macros that evaluate an argument more than once with a `static inline` function
- Flag every `#ifdef`/`#ifndef` beyond an include guard and require a comment justifying it
- Never let `#ifdef` change a function's signature across translation units

## Violation

```c
#define SQUARE(x) ((x) * (x))

int compute(int i) {
    int n = SQUARE(i++);
    return n;
}
```

## Fix

```c
static inline int square(int x) {
    return x * x;
}

int compute(int i) {
    int n = square(i++);
    return n;
}
```

## Tooling
- `clang-tidy`: `cppcoreguidelines-macro-usage` - flags constants and function-like macros that should be typed constants or functions instead
- `clang-tidy`: `bugprone-macro-parentheses` - catches missing parens around macro parameters/body that let operator precedence corrupt an expansion
- `clang-tidy`: `bugprone-reserved-identifier` - flags identifiers, including macro names, that start with a reserved underscore prefix
- `cppcheck --enable=all`: manual review of flagged macro expansions for side-effect risk
- `manual review`: grep for `#ifdef` outside include guards; each hit needs a justifying comment

## Strict profile
STRICT C promotes `bugprone-macro-parentheses` from a `clang-tidy` advisory to a CI-failing error, per the shared strict gate list. Any `#ifdef` beyond an include guard fails CI without a documented justification comment.
