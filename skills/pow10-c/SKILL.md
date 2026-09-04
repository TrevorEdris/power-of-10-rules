---
name: pow10-c
description: Use when writing, editing, refactoring, or reviewing C code (.c and .h files, embedded or firmware modules, PR diffs) and before declaring a C task done. Applies the ten NASA Power of 10 rules in their original literal form as a checklist with clang-tidy and cppcheck enforcement. This is the canonical reference the Go and Python profiles adapt from.
---

# pow10-c

Type: flexible in wording, literal in substance. The rules were written for C; the checklist below is the literal profile and every item is enforced as written.

Announce once per task: `Using pow10-c to check <target> against the Power of 10 (literal profile).`

## When this applies

- You are writing or editing `.c` or `.h` files, or reviewing a C diff.
- The literal rules are the default for C. `--strict` adds the CI gates in the Strict profile section.
- Whole directory, PR, or multi-file diff: dispatch the `pow10-auditor` agent with the scope instead of checking inline.

## Checklist (literal profile)

Severity in brackets. Open the linked reference only when its "read when" condition holds.

### Rule 1 - Simple control flow [blocker]
- No `goto`, `setjmp`, or `longjmp`. Cleanup uses structured flow, not non-local jumps.
- No recursion, direct or indirect, including mutual recursion across translation units.
- Read when a function calls itself or uses a non-local jump: `references/rule-01-control-flow.md`

### Rule 2 - Bounded loops [blocker]
- Every loop has a statically verifiable upper bound, a compile-time constant where possible.
- A bound derived from runtime input is asserted against a fixed maximum before the loop.
- `for (;;)` appears only in the one annotated main scheduler loop.
- Read when you write `while`, `for (;;)`, or a loop over a runtime-sized buffer: `references/rule-02-bounded-loops.md`

### Rule 3 - No dynamic memory after initialization [blocker]
- No `malloc`, `calloc`, `realloc`, `free`, or `alloca` after the initialization phase.
- Memory comes from fixed pools, the stack, or static buffers. Worst-case usage is computable at build time.
- Read when you allocate, or when the init boundary is unclear: `references/rule-03-no-dynamic-memory.md`

### Rule 4 - Short functions [high]
- Each function fits on one printed page: hard limit 60 source lines, soft limit 40.
- One responsibility per function. Decompose instead of nesting past 3 levels.
- Read when a function crosses 40 lines: `references/rule-04-short-functions.md`

### Rule 5 - Assertion density [high]
- At least two runtime assertions per function on average across the translation unit.
- Assertions are side-effect free and stay active in release builds with a defined recovery path.
- Read when you write a function with no precondition or invariant check: `references/rule-05-assertion-density.md`

### Rule 6 - Minimum scope [medium]
- Every variable is declared at the narrowest scope that uses it.
- No mutable globals or file-scope statics. When unavoidable, `const` or a documented access protocol.
- Read when you add a file-scope object or an `extern`: `references/rule-06-minimum-scope.md`

### Rule 7 - Check return values and parameters [blocker]
- Every non-void return value is checked, or explicitly cast to `(void)` with a comment stating why.
- Every parameter is validated at function entry before any state mutation.
- Read when you call a function that returns a status, or write a function that mutates before it validates: `references/rule-07-check-return-values.md`

### Rule 8 - Limited preprocessor [high]
- Preprocessor use is limited to `#include`, object-like constants, and narrow `#ifdef` for platform differences.
- No token pasting, stringification, recursive or variadic macros, or function-like macros with side-effect risk.
- Read when you write `#define` with parameters or `##`: `references/rule-08-limited-preprocessor.md`

### Rule 9 - Restricted pointers [blocker]
- At most one level of dereferencing per declaration; no `**`.
- Pointer dereferences are not hidden inside macro definitions or `typedef` declarations.
- No function pointers, except one documented and isolated interrupt vector table.
- Read when you write `**`, a function pointer type, or a macro that dereferences: `references/rule-09-restrict-pointers.md`

### Rule 10 - Warnings as errors [blocker]
- `-Wall -Wextra -Wpedantic -Werror` (plus `-Wshadow -Wconversion`) on every build.
- CI runs at least one analyzer beyond the compiler (`clang-tidy`, `cppcheck`) and fails on findings.
- Every suppression names the check and a reason.
- Read when touching build flags, CI, or a suppression: `references/rule-10-warnings-as-errors.md`

## Reporting while editing

- Fix trivially fixable findings in code you are already changing; mention it in one line.
- Otherwise report one line per finding: `pow10 R2 [blocker] src/uart.c:118 - while loop bound depends on rx_len with no maximum - assert rx_len <= RX_MAX before the loop`.
- Blockers stop the task until fixed or the user overrides. Medium findings are listed and the task continues.
- Do not review code you were not asked to touch. Suggest `/pow10-review <scope>` instead.

## Strict profile

The checklist above is already literal. `--strict` additionally requires the CI gates: `clang-tidy` with `misc-no-recursion`, `cppcoreguidelines-avoid-goto`, `cppcoreguidelines-no-malloc`, `readability-function-size`, `bugprone-assert-side-effect`, `cppcoreguidelines-avoid-non-const-global-variables`, `bugprone-macro-parentheses`, and `bugprone-unused-return-value` promoted to errors; `cppcheck --enable=all --error-exitcode=1`; a second analyzer from a different vendor. Prefix findings with `[STRICT]`.

## Rationalizations

| Excuse | Reality |
| --- | --- |
| "The buffer is always big enough." | Then assert the bound. An unstated bound is a missing one. |
| "This macro is just a shortcut." | A macro with an argument is a function without a type check. |
| "`(void)` is fine, the call cannot fail." | Write the reason next to it. The next reader cannot see your certainty. |
| "The auditor will catch it later." | The auditor reads this same list. Catching it now is cheaper. |

## Tooling baseline

`gcc`/`clang` with `-Wall -Wextra -Wpedantic -Werror -Wshadow -Wconversion`; `clang-tidy` with the checks named above; `cppcheck --enable=all --error-exitcode=1`. Config example: `references/rule-10-warnings-as-errors.md`.
