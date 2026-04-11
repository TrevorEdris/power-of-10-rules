---
name: pow10-rule-07-check-return-values
description: "NASA Power of 10 Rule 7: Check the return value of every non-void function and validate every parameter (severity: blocker)"
---

# Rule 7: Check the return value of every non-void function and validate every parameter

**Severity:** blocker

## Rationale

Ignoring a return value discards error information the callee spent effort computing. A function that returns a status code but is called with `(void)foo()` indicates a silent failure path. Parameters must be validated at function entry — callers cannot be trusted, even within the same module. Both checks combine to isolate errors at their source instead of letting them propagate into corrupted state.

## Enforcement

**Strategy:** static-analysis
**Tools:** clang-tidy, cppcheck

Clang-tidy checks: bugprone-unused-return-value, bugprone-argument-comment, cert-err33-c. Explicit `(void)foo()` casts are allowed but must carry a comment justifying why the return value is safe to ignore. Parameter validation must happen before any state mutation.

## Citations

- **Holzmann 2006** — Rule 7, The Power of 10: Rules for Developing Safety-Critical Code, IEEE Computer 39(6), 95-97
- **CERT C Secure Coding Standard** — ERR33-C: Detect and handle standard library errors
