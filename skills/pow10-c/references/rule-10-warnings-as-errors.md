# Rule 10 - Warnings As Errors (C)

**Statement (Holzmann):** Compile with the strictest warning flags the toolchain offers, and treat every warning as a build failure - fix the code, never suppress the message.

**Profile (literal):** applies fully; severity **blocker**.

The literal rule is the strict bar: `-Wall -Wextra -Wpedantic -Werror` plus the safety-relevant extras, gated in CI with zero warnings tolerated. Beyond Holzmann's compiler-only text, this plugin also requires a second, independently-sourced static analyzer (clang-tidy or cppcheck) in the same CI gate - an explicit extension, not part of the original rule. A single missed warning can hide uninitialized memory, a format-string mismatch, or a silent truncation that corrupts control flow.

## Checklist
- Enable `-Wall -Wextra -Wpedantic -Werror` (or equivalent) on every compile target
- Add `-Wshadow -Wconversion` to the warning set
- Fail CI on any compiler warning, not just errors
- Run clang-tidy or cppcheck as a second analyzer in the same CI job
- Scope every suppression to one line or block and state the reason inline
- Do not merge a change that introduces a new warning, even if the build "passes"

## Violation

```c
#include <stdio.h>

int compute(int a, int b) {
    int result;
    if (a > b) {
        result = a - b;
    }
    return result;
}

int main(void) {
    printf("%d\n", compute(3, 5));
    return 0;
}
```

## Fix

```c
#include <stdio.h>

int compute(int a, int b) {
    int result = 0;
    if (a > b) {
        result = a - b;
    }
    return result;
}

int main(void) {
    printf("%d\n", compute(3, 5));
    return 0;
}
```

## Tooling
- `gcc`/`clang`: `-Wall -Wextra -Wpedantic -Werror` - fails the build on any warning, catches uninitialized reads like the example above
- `clang-tidy`: `bugprone-suspicious-string-compare`, `cert-err33-c` - second analyzer, catches misuse patterns the compiler warning set misses
- `cppcheck`: `--enable=all --error-exitcode=1` - second analyzer, flags issues like unread stores (`unreadVariable`) the compiler may not

## Strict profile
CI gate: `gcc -Wall -Wextra -Wpedantic -Werror -Wshadow -Wconversion`, plus `cppcheck --enable=all --error-exitcode=1` and a second analyzer from a different vendor (`clang-tidy`) in the same job; any nonzero exit aborts the merge.
