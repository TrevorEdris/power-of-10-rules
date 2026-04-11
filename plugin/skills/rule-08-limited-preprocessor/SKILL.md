---
name: pow10-rule-08-limited-preprocessor
description: "NASA Power of 10 Rule 8: Limit preprocessor use to header inclusion and simple macros (severity: high)"
---

# Rule 8: Limit preprocessor use to header inclusion and simple macros

**Severity:** high

## Rationale

The C preprocessor is not part of the language grammar and runs before the compiler sees the source. Aggressive preprocessor use — token pasting, recursive macros, conditional compilation that varies symbol meaning across files — defeats static analysis, confuses debuggers, and produces code that is unreadable without running cpp by hand. Restrict preprocessor use to `#include`, simple object-like macros for constants, and narrow `#ifdef` gates for platform differences.

## Enforcement

**Strategy:** static-analysis
**Tools:** clang-tidy, manual-review

Forbid token-pasting (##), stringification (#), recursive/variadic macros, and conditional compilation that changes function signatures. Prefer `static const` and inline functions over function-like macros. Clang-tidy checks: cppcoreguidelines-macro-usage, bugprone-macro-parentheses.

## Citations

- **Holzmann 2006** — Rule 8, The Power of 10: Rules for Developing Safety-Critical Code, IEEE Computer 39(6), 95-97
