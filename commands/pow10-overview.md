---
description: Show the NASA Power of 10 rules index with severities and per-rule skill names.
---

Display the NASA Power of 10 rules index. Format as a table with columns: rule number, statement (one line), severity (blocker/high/medium), skill name to load for full guidance.

After the table, briefly explain:
- When to apply (safety-critical: firmware, flight, medical, automotive)
- When NOT to apply (rich-runtime application code)
- The inline waiver convention: `// pow10: allow rule=N until=YYYY-MM-DD owner=<handle> reason="..."` (use the language's native comment syntax)
- That the per-rule skills (`pow10-rule-NN-...`) cover C, Go, Python, Java, Kotlin
- That `/pow10-review` runs a full pass against a file or diff

Cite Holzmann (2006) and the JPL Institutional Coding Standard at the end.

Keep it terse — under 30 lines of output.
