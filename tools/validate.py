#!/usr/bin/env python3
"""Structural validator for the pow10 plugin.

Usage:
  python3 tools/validate.py                 # whole repo
  python3 tools/validate.py --ref FILE...   # one or more reference files only

Exit 0 and print OK when clean; otherwise print one problem per line and exit 1.
Stdlib only. Tool-name checks use the verified lists in tools/verified/ when present.
"""
from __future__ import annotations

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERIFIED_DIRS = [
    os.path.join(ROOT, "tools", "verified"),
    os.path.join(
        os.path.expanduser("~"),
        "src/.ai/sessions/2026-09-04_power10_Plugin-Audit-And-Cohesion-Plan/verified",
    ),
]

LANGS = {"go": "Go", "python": "Python", "c": "C"}
SLUGS = [
    "01-control-flow",
    "02-bounded-loops",
    "03-no-dynamic-memory",
    "04-short-functions",
    "05-assertion-density",
    "06-minimum-scope",
    "07-check-return-values",
    "08-limited-preprocessor",
    "09-restrict-pointers",
    "10-warnings-as-errors",
]
SEVERITY = {  # rule -> (go, python, c)
    "01": ("medium", "medium", "blocker"),
    "02": ("medium", "medium", "blocker"),
    "03": ("advisory", "advisory", "blocker"),
    "04": ("medium", "medium", "high"),
    "05": ("advisory", "medium", "high"),
    "06": ("medium", "medium", "medium"),
    "07": ("blocker", "high", "blocker"),
    "08": ("medium", "high", "high"),
    "09": ("medium", "advisory", "blocker"),
    "10": ("high", "medium", "blocker"),
}
FORBIDDEN = [
    "pow10: allow", "Waiver", "waiver", "Java", "Kotlin", "Cursor", "Codex",
    ".pow10.json", "exportloopref", "PGH001", "ANN101", "cert-err52-cpp",
    "cert-msc54-cpp", "MicroPython", "until=", "owner=",
]
REF_HEADINGS = ["## Checklist", "## Violation", "## Fix", "## Tooling", "## Strict profile"]
TOOL_ALLOW = {
    "golangci-lint", "staticcheck", "go", "go vet", "go build", "go test", "gofmt", "govet",
    "ruff", "mypy", "pyright", "pylint", "bandit", "cppcheck", "clang-tidy", "clang", "gcc",
    "lizard", "pytest", "python", "python3", "manual review", "code review", "go vet ./...",
    "golangci-lint run", "ruff check", "mypy --strict", "cppcheck --enable=all",
    "clang-tidy --warnings-as-errors=*", "gocyclo", "gocognit", "funlen", "nestif",
    "errcheck", "gosec", "revive", "unused", "ineffassign", "prealloc", "wrapcheck",
    "errorlint", "copyloopvar", "gochecknoglobals", "gochecknoinits", "nilerr", "gocritic",
    "go vet -copylocks", "go test -race", "-race", "-Wall", "-Wextra", "-Werror",
    "-Wpedantic", "-Wshadow", "-Wconversion", "-Wcast-align", "-Wstrict-prototypes",
    "-fanalyzer", "-fsanitize=address,undefined", "pyproject.toml", ".golangci.yml",
}


def load_list(name: str) -> set[str] | None:
    for d in VERIFIED_DIRS:
        p = os.path.join(d, name)
        if os.path.exists(p):
            return {line.strip() for line in open(p) if line.strip()}
    return None


LISTS = {
    "golangci": load_list("golangci-linters.txt"),
    "staticcheck": load_list("staticcheck-checks.txt"),
    "ruff": load_list("ruff-rules.txt"),
    "pylint": load_list("pylint-msgs.txt"),
    "clangtidy": load_list("clang-tidy-checks.txt"),
    "cppcheck": load_list("cppcheck-ids.txt"),
}


def frontmatter(text: str) -> tuple[dict, str]:
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        return {}, text
    d = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            d[k.strip()] = v.strip().strip('"').strip("'")
    return d, m.group(2)


def check_forbidden(path: str, text: str, out: list[str]) -> None:
    for s in FORBIDDEN:
        if s in text:
            out.append(f"{path}: forbidden string {s!r}")


def check_links(path: str, text: str, out: list[str]) -> None:
    for link in re.findall(r"\]\(([^)#\s]+)\)", text):
        if link.startswith(("http://", "https://", "mailto:")):
            continue
        tgt = os.path.normpath(os.path.join(os.path.dirname(path), link))
        if not os.path.exists(tgt):
            out.append(f"{path}: broken relative link {link}")


def check_tool_token(lang: str, tok: str, path: str, out: list[str]) -> None:
    if tok in TOOL_ALLOW or tok.startswith("-") or tok.startswith("go vet"):
        return
    m_sc = re.fullmatch(r"(SA|ST|S|QF)\d{4}", tok)
    m_ruff = re.fullmatch(r"[A-Z]{1,4}\d{3,4}", tok)
    m_pylint = re.fullmatch(r"[CRWEF]\d{4}", tok)
    m_ct = re.fullmatch(r"(abseil|altera|android|boost|bugprone|cert|clang-analyzer|concurrency|cppcoreguidelines|darwin|fuchsia|google|hicpp|linuxkernel|llvm|llvmlibc|misc|modernize|mpi|objc|openmp|performance|portability|readability|zircon)-[a-z0-9.-]+", tok)
    if lang == "go" and m_sc:
        if LISTS["staticcheck"] is not None and tok not in LISTS["staticcheck"]:
            out.append(f"{path}: unknown staticcheck check {tok}")
        return
    if lang == "python" and m_pylint and LISTS["pylint"] is not None and tok in LISTS["pylint"]:
        return
    if lang == "python" and m_ruff:
        if LISTS["ruff"] is not None and tok not in LISTS["ruff"]:
            out.append(f"{path}: unknown ruff rule {tok}")
        return
    if lang == "c" and m_ct:
        if LISTS["clangtidy"] is not None and tok not in LISTS["clangtidy"]:
            out.append(f"{path}: unknown clang-tidy check {tok}")
        return
    if lang == "go" and re.fullmatch(r"[a-z][a-z0-9]+", tok):
        if LISTS["golangci"] is not None and tok not in LISTS["golangci"]:
            out.append(f"{path}: unknown golangci-lint linter {tok}")
        return
    if lang == "c" and re.fullmatch(r"[a-z][A-Za-z]+", tok):
        if LISTS["cppcheck"] is not None and tok not in LISTS["cppcheck"]:
            out.append(f"{path}: unverified cppcheck id {tok} (cite `cppcheck --enable=all` instead)")
        return
    # anything else in backticks inside Tooling: config keys, flags with spaces, etc. are tolerated


def check_ref(path: str, out: list[str]) -> None:
    rel = os.path.relpath(path, ROOT)
    m = re.search(r"skills/pow10-(go|python|c)/references/rule-(\d\d)-([a-z0-9-]+)\.md$", rel)
    if not m:
        out.append(f"{rel}: not a reference path")
        return
    lang, num, slug = m.group(1), m.group(2), m.group(3)
    if f"{num}-{slug}" not in SLUGS:
        out.append(f"{rel}: unknown slug {num}-{slug}")
    text = open(path, encoding="utf-8").read()
    lines = text.splitlines()
    n = len(lines)
    if not 35 <= n <= 100:
        out.append(f"{rel}: {n} lines (want 35-100)")
    if not re.match(rf"^# Rule {int(num)} - .+ \({LANGS[lang]}\)$", lines[0] if lines else ""):
        out.append(f"{rel}: first line must be '# Rule {int(num)} - <Title> ({LANGS[lang]})'")
    if not re.search(r"^\*\*Statement \(Holzmann\):\*\* \S", text, re.M):
        out.append(f"{rel}: missing '**Statement (Holzmann):** ...' line")
    kind = "literal" if lang == "c" else "adapted"
    pm = re.search(r"^\*\*Profile \((adapted|literal)\):\*\* applies (fully|partially|in spirit|not applicable); severity \*\*(blocker|high|medium|advisory)\*\*\.$", text, re.M)
    if not pm:
        out.append(f"{rel}: missing/malformed '**Profile ({kind}):** applies ...; severity **...**.' line")
    else:
        if pm.group(1) != kind:
            out.append(f"{rel}: profile must be ({kind})")
        want = SEVERITY[num][{"go": 0, "python": 1, "c": 2}[lang]]
        if pm.group(3) != want:
            out.append(f"{rel}: severity {pm.group(3)} but plan matrix says {want}")
    h2 = [ln for ln in lines if ln.startswith("## ")]
    if h2 != REF_HEADINGS:
        out.append(f"{rel}: ## headings must be exactly {REF_HEADINGS}, got {h2}")
    # sections
    def section(name: str) -> str:
        i = text.find(name)
        if i < 0:
            return ""
        j = text.find("\n## ", i + 1)
        return text[i:j if j > 0 else len(text)]
    bullets = [ln for ln in section("## Checklist").splitlines() if ln.startswith("- ")]
    if not 3 <= len(bullets) <= 6:
        out.append(f"{rel}: Checklist has {len(bullets)} bullets (want 3-6)")
    tag = {"go": "go", "python": "python", "c": "c"}[lang]
    for sec in ("## Violation", "## Fix"):
        blocks = re.findall(r"```(\w*)\n(.*?)```", section(sec), re.S)
        if len(blocks) != 1:
            out.append(f"{rel}: {sec} must contain exactly one fenced block (got {len(blocks)})")
            continue
        t, body = blocks[0]
        if t != tag:
            out.append(f"{rel}: {sec} fence tag must be {tag}")
        bl = body.strip("\n").count("\n") + 1
        if not 5 <= bl <= 20:
            out.append(f"{rel}: {sec} block is {bl} lines (want 5-20)")
        if "..." in body and lang != "go":
            out.append(f"{rel}: {sec} contains placeholder '...'")
    tool_sec = section("## Tooling")
    tb = [ln for ln in tool_sec.splitlines() if ln.startswith("- ")]
    if not tb:
        out.append(f"{rel}: Tooling has no bullets")
    for ln in tb:
        if not re.match(r"^- `[^`]+`", ln):
            out.append(f"{rel}: Tooling bullet must start with a backticked tool: {ln[:60]}")
        for tok in re.findall(r"`([^`]+)`", ln):
            check_tool_token(lang, tok, rel, out)
    sp = section("## Strict profile")
    body_lines = [ln for ln in sp.splitlines()[1:] if ln.strip()]
    if not 1 <= len(body_lines) <= 4:
        out.append(f"{rel}: Strict profile must be 1-4 non-empty lines (got {len(body_lines)})")
    if "—" in text:
        out.append(f"{rel}: contains an em dash; use ' - '")
    check_forbidden(rel, text, out)
    check_links(path, text, out)


def check_skill(path: str, out: list[str]) -> None:
    rel = os.path.relpath(path, ROOT)
    text = open(path, encoding="utf-8").read()
    fm, body = frontmatter(text)
    d = os.path.basename(os.path.dirname(path))
    if fm.get("name") != d:
        out.append(f"{rel}: frontmatter name {fm.get('name')!r} != directory {d!r}")
    desc = fm.get("description", "")
    if not desc:
        out.append(f"{rel}: missing description")
    if len(desc) > 400:
        out.append(f"{rel}: description {len(desc)} chars (max 400)")
    if "Use when" not in desc:
        out.append(f"{rel}: description must contain 'Use when'")
    n = text.count("\n")
    if n > 200:
        out.append(f"{rel}: {n} lines (max 200)")
    if d == "pow10":
        if fm.get("disable-model-invocation") != "true":
            out.append(f"{rel}: overview must set disable-model-invocation: true")
    else:
        lang = d.replace("pow10-", "")
        for s in SLUGS:
            if f"references/rule-{s}.md" not in body:
                out.append(f"{rel}: does not point to references/rule-{s}.md")
        if "Using pow10-" not in body:
            out.append(f"{rel}: missing announce line 'Using pow10-{lang} ...'")
    if "—" in text:
        out.append(f"{rel}: contains an em dash; use ' - '")
    check_forbidden(rel, text, out)
    check_links(path, text, out)


def check_agent_and_command(out: list[str]) -> None:
    a = os.path.join(ROOT, "agents", "pow10-auditor.md")
    if not os.path.exists(a):
        out.append("agents/pow10-auditor.md: missing")
    else:
        text = open(a, encoding="utf-8").read()
        fm, body = frontmatter(text)
        for k in ("name", "description", "model"):
            if not fm.get(k):
                out.append(f"agents/pow10-auditor.md: frontmatter missing {k}")
        for h in ("## Advisory", "[STRICT]", "## Procedure"):
            if h not in body:
                out.append(f"agents/pow10-auditor.md: missing {h!r}")
        check_forbidden("agents/pow10-auditor.md", text, out)
    c = os.path.join(ROOT, "commands", "pow10-review.md")
    if not os.path.exists(c):
        out.append("commands/pow10-review.md: missing")
    else:
        text = open(c, encoding="utf-8").read()
        fm, body = frontmatter(text)
        if not fm.get("argument-hint"):
            out.append("commands/pow10-review.md: missing argument-hint")
        if "$ARGUMENTS" not in body:
            out.append("commands/pow10-review.md: body must use $ARGUMENTS")
        bl = len([ln for ln in body.splitlines() if ln.strip()])
        if bl > 15:
            out.append(f"commands/pow10-review.md: body has {bl} non-empty lines (max 15)")
        if "pow10-auditor" not in body:
            out.append("commands/pow10-review.md: must dispatch pow10-auditor")
        check_forbidden("commands/pow10-review.md", text, out)
    if os.path.exists(os.path.join(ROOT, "commands", "pow10-overview.md")):
        out.append("commands/pow10-overview.md: must be removed (overview is a skill now)")


def check_tree(out: list[str]) -> None:
    for d in ("pow10", "pow10-go", "pow10-python", "pow10-c"):
        p = os.path.join(ROOT, "skills", d, "SKILL.md")
        if not os.path.exists(p):
            out.append(f"skills/{d}/SKILL.md: missing")
        else:
            check_skill(p, out)
    for lang in LANGS:
        for s in SLUGS:
            p = os.path.join(ROOT, "skills", f"pow10-{lang}", "references", f"rule-{s}.md")
            if not os.path.exists(p):
                out.append(f"skills/pow10-{lang}/references/rule-{s}.md: missing")
            else:
                check_ref(p, out)
    if os.path.exists(os.path.join(ROOT, "skills", "pow10", "references")):
        out.append("skills/pow10/references: overview must not have a references dir")
    for stale in [d for d in os.listdir(os.path.join(ROOT, "skills")) if d.startswith("pow10-rule-")]:
        out.append(f"skills/{stale}: old per-rule directory still present")
    for doc in ("README.md", "CONTRIBUTING.md"):
        p = os.path.join(ROOT, doc)
        if os.path.exists(p):
            text = open(p, encoding="utf-8").read()
            check_forbidden(doc, text, out)
            check_links(p, text, out)
    check_agent_and_command(out)


def main(argv: list[str]) -> int:
    out: list[str] = []
    if len(argv) >= 2 and argv[1] == "--ref":
        for p in argv[2:]:
            check_ref(os.path.abspath(p), out)
    else:
        check_tree(out)
    if out:
        print("\n".join(out))
        print(f"{len(out)} problem(s)")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
