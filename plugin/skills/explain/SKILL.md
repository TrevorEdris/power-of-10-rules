---
name: pow10-explain
description: Explain a NASA Power of 10 rule in detail, with rationale and enforcement guidance.
---

## What this skill does

Prints the full text of one of the 10 Power of 10 rules: name, rationale,
severity, enforcement strategy, recommended tools, and citations.

## How to invoke

```
pow10 explain <N>
```

Where `<N>` is a rule number between 1 and 10.

## Example

```
$ pow10 explain 2
Rule 2: All loops must have a statically determinable upper bound
Severity: blocker
...
```

## Status

`pow10 explain` is **fully implemented** in M2. This is the exit criterion
for the milestone.
