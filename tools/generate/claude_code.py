"""Claude Code plugin renderer.

Pure functions — take dataclasses / strings, return strings. No I/O.
tools/generate.py is the only module that writes files.

Public API:
  RULE_SLUGS              — {1: "control-flow", 2: ...} maps rule number to kebab slug
  META_SKILLS             — {"audit": (description, body), ...} for the 7 meta skills
  render_rule_skill(rule) — str: SKILL.md content for a per-rule skill
  render_meta_skill(name) — str: SKILL.md content for a meta skill
  render_subagent()       — str: agents/pow10-auditor.md content
"""

from typing import Dict, Tuple

# Stable kebab slugs for each of the 10 rules. Hardcoded rather than derived
# from the rule name so minor wording tweaks to core/rules/c/rule-*.json do not
# rename skill directories (which would break user muscle memory and marketplace
# discovery). 10 rules, rarely change. Keep in sync with core/rules/c/rule-*.json.
RULE_SLUGS: Dict[int, str] = {
    1: "control-flow",
    2: "bounded-loops",
    3: "no-dynamic-memory",
    4: "short-functions",
    5: "assertion-density",
    6: "minimum-scope",
    7: "check-return-values",
    8: "limited-preprocessor",
    9: "restrict-pointers",
    10: "warnings-as-errors",
}


# Meta skills. Each tuple is (description, body). The body is an instructional
# markdown block that tells Claude Code (and by extension the user) what the
# skill does and which `pow10` CLI subcommand it delegates to. M2 ships full
# instructional text for all 7; only `explain` has a working runtime. The
# others delegate to CLI stubs that print "not yet implemented (lands in Mx)".
META_SKILLS: Dict[str, Tuple[str, str]] = {
    "audit": (
        "Run pow10 audit across the current repo and report violations of NASA Power of 10 rules.",
        """## What this skill does

Invoke `pow10 audit` to scan the current repository for violations of the
NASA Power of 10 safety-critical coding rules. The audit runs language-specific
static analyzers, normalizes findings, and folds in inline waivers.

## When to use

- Before merging a PR that touches safety-critical code
- As part of a release checklist
- When onboarding a new module into the pow10 discipline

## How to invoke

```
pow10 audit [--path <dir>] [--language c]
```

## Status

Audit runtime lands in **M3** (C analyzer) and **M5** (Go / Python / Kotlin / Java).
Running `pow10 audit` today returns a `not yet implemented` stub.
""",
    ),
    "fix": (
        "Remediate a single pow10 audit finding with a minimal diff.",
        """## What this skill does

Given a specific audit finding (file + line + rule), produce a minimal,
reviewable patch that resolves the violation without introducing new ones.

## How to invoke

```
pow10 fix <file>:<line> --rule <N>
```

## Status

`pow10 fix` runtime lands in **M3**. Current implementation is a stub.
""",
    ),
    "onboard": (
        "Interactively scaffold .pow10.json, CI wiring, and init-phase markers for a new repo.",
        """## What this skill does

Walks the user through adopting pow10 in a new repository:
- Creates `.pow10.json` with detected languages
- Offers to install a CI workflow for `pow10 audit`
- Adds `pow10:init-end` markers to `main()` so Rule 3 knows where the init phase ends
- Lists missing host analyzers with install commands (never auto-installs)
- Offers to copy `cursor/.cursor/rules/*` into the repo (Cursor users)
- Offers to install Codex user-level prompts (Codex CLI users)

## How to invoke

```
pow10 onboard
```

## Status

`pow10 onboard` lands in **M3**. Stub today.
""",
    ),
    "report": (
        "Produce a JPL LOC-1..LOC-4 compliance report for the current repo.",
        """## What this skill does

Aggregates the results of `pow10 audit` into a JPL-style compliance report:
- LOC-1: critical compliance (blocker rules)
- LOC-2: standard compliance (high-severity rules)
- LOC-3: advisory (medium)
- LOC-4: informational (low)

Folds inline waivers into the counts and flags expired waivers separately.

## How to invoke

```
pow10 report [--format markdown|json]
```

## Status

`pow10 report` lands in **M3**. Stub today.
""",
    ),
    "waive": (
        "Author a well-formed inline waiver comment at a specific violation site.",
        """## What this skill does

Writes a `pow10: allow` inline comment at a specified file:line with the
correct comment syntax for the file's language. Prompts for:
- `owner` — engineer accepting the waiver
- `until` — expiry date (YYYY-MM-DD)
- `reason` — free-text justification

No statefile — waivers live next to the code they waive.

## How to invoke

```
pow10 waive <file>:<line> --rule <N>
```

## Status

`pow10 waive` lands in **M3**. Stub today.
""",
    ),
    "list-waivers": (
        "Walk the repo and list every active pow10 inline waiver with its expiry.",
        """## What this skill does

Scans all source files under the current directory, finds every inline
`pow10: allow` comment, and reports:
- File + line
- Rule number
- Owner handle
- Expiry date (YYYY-MM-DD)
- Days remaining (negative = expired)

Expired waivers are flagged prominently.

## How to invoke

```
pow10 list-waivers [--path <dir>]
```

## Status

`pow10 list-waivers` lands in **M3**. Stub today.
""",
    ),
    "explain": (
        "Explain a NASA Power of 10 rule in detail, with rationale and enforcement guidance.",
        """## What this skill does

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
""",
    ),
}


def _yaml_escape(value: str) -> str:
    """Minimal YAML-safe single-line string encoding.

    We only need scalars inside frontmatter. If the string contains a colon,
    quote it. Backslashes and quotes are escaped. Newlines are rejected —
    frontmatter values here are always single-line.
    """
    if "\n" in value:
        raise ValueError(f"multiline strings not supported in frontmatter: {value!r}")
    if ":" in value or '"' in value or value.startswith(("'", "[", "{", "&", "*", "#", "?", "|", "-", "<", ">", "=", "!", "%", "@", "`")):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return value


def _render_frontmatter(name: str, description: str) -> str:
    return (
        "---\n"
        f"name: {_yaml_escape(name)}\n"
        f"description: {_yaml_escape(description)}\n"
        "---\n"
    )


def render_rule_skill(rule) -> str:  # type: ignore[no-untyped-def]
    """Render a per-rule SKILL.md for a loaded Rule dataclass.

    Minimal content per M2 design decision #2: rule text, rationale, severity,
    enforcement strategy / tools / notes, citations. No examples — language-
    specific example blocks land in M4 when per-language content is added.
    """
    slug = RULE_SLUGS[rule.number]
    description = (
        f"NASA Power of 10 Rule {rule.number}: {rule.name} (severity: {rule.severity})"
    )
    frontmatter = _render_frontmatter(
        name=f"pow10-rule-{rule.number:02d}-{slug}",
        description=description,
    )

    tools_line = ", ".join(rule.enforcement.tools) if rule.enforcement.tools else "—"
    citations_lines = [
        f"- **{c.source}** — {c.reference}" for c in rule.citations
    ]

    body = "\n".join(
        [
            f"# Rule {rule.number}: {rule.name}",
            "",
            f"**Severity:** {rule.severity}",
            "",
            "## Rationale",
            "",
            rule.rationale,
            "",
            "## Enforcement",
            "",
            f"**Strategy:** {rule.enforcement.strategy}",
            f"**Tools:** {tools_line}",
            "",
            rule.enforcement.notes,
            "",
            "## Citations",
            "",
            *citations_lines,
            "",
        ]
    )

    return frontmatter + "\n" + body


def render_meta_skill(name: str) -> str:
    """Render a meta-skill SKILL.md (audit, fix, onboard, etc.)."""
    description, body = META_SKILLS[name]
    frontmatter = _render_frontmatter(name=f"pow10-{name}", description=description)
    return frontmatter + "\n" + body


def render_subagent() -> str:
    """Render plugin/agents/pow10-auditor.md.

    M2 ships a skeleton that delegates to `pow10 audit` (which itself stubs
    until M3). M8 flips the subagent into its hook-integrated form.
    """
    frontmatter = _render_frontmatter(
        name="pow10-auditor",
        description="Runs pow10 audit on the current repo and reports NASA Power of 10 violations.",
    )
    body = """# pow10-auditor

## Role

You are a focused audit agent. Your job is to run `pow10 audit` on the
current working directory, interpret the findings, and report them to the
user with actionable remediation steps.

## Instructions

1. Detect the project languages from the file tree.
2. Invoke `pow10 audit` with appropriate flags.
3. Parse the JSON output.
4. Group findings by rule number and severity.
5. For each finding, suggest the specific fix (quote the relevant pow10 rule text).
6. Flag any inline waivers near expiry.

## Status

Skeleton only — M2 ships this file so plugin surfaces and marketplace manifest
can reference a stable path. The actual audit runtime and hook integration
land in **M3** (C analyzer) and **M8** (PostToolUse hook + subagent wiring).
"""
    return frontmatter + "\n" + body
