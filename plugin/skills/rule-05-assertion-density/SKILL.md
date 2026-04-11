---
name: pow10-rule-05-assertion-density
description: "NASA Power of 10 Rule 5: Use a minimum of two runtime assertions per function on average (severity: high)"
---

# Rule 5: Use a minimum of two runtime assertions per function on average

**Severity:** high

## Rationale

Assertions catch anomalies that static analysis cannot: violated preconditions, impossible states, and invariants broken by unexpected input. A density of roughly two assertions per function forces the author to think through what must be true at each boundary. Assertions must have no side effects and must behave deterministically in both debug and release builds — a failed assertion should trigger a defined recovery path, not silent continuation.

## Enforcement

**Strategy:** metric
**Tools:** custom-metric

Count assert() invocations per function; average across the translation unit must be >= 2. Assertions with side effects (e.g. `assert(x++ > 0)`) are flagged as errors. In release builds, assertions should compile to a recovery call rather than being stripped entirely.

## Citations

- **Holzmann 2006** — Rule 5, The Power of 10: Rules for Developing Safety-Critical Code, IEEE Computer 39(6), 95-97
