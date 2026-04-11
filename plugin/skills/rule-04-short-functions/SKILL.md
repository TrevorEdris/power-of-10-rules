---
name: pow10-rule-04-short-functions
description: "NASA Power of 10 Rule 4: Keep functions short enough to print on one sheet of paper (severity: high)"
---

# Rule 4: Keep functions short enough to print on one sheet of paper

**Severity:** high

## Rationale

A function that fits on a single printed page (roughly 60 lines including declarations and whitespace) can be understood and reviewed as a unit. Longer functions indicate that the author conflated multiple logical tasks, which increases review cost, hides bugs, and makes unit testing harder. Short functions align with the single-responsibility principle and compose into larger units through readable call sites.

## Enforcement

**Strategy:** metric
**Tools:** clang-tidy, lizard

Hard limit: 60 source lines per function (excluding comments). Soft limit: 40 lines. Clang-tidy check: readability-function-size with `LineThreshold: 60`. Functions exceeding the hard limit must either be decomposed or carry a documented waiver.

## Citations

- **Holzmann 2006** — Rule 4, The Power of 10: Rules for Developing Safety-Critical Code, IEEE Computer 39(6), 95-97
