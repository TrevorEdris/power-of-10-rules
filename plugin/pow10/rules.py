"""Rule dataclasses, JSON loader, and schema validator.

Stdlib-only. No pydantic, no jsonschema. Uses `dataclasses` for the data model
and a minimal hand-rolled subset of JSON Schema validation in `validate_rule`.

Layer model:
  - Citation, Enforcement, Rule  — frozen dataclasses, the in-memory form
  - load_rule(path)              — JSON file -> Rule (runs validate_rule first)
  - validate_rule(data)          — raw dict -> list of error strings (empty = valid)
  - load_schema()                — reads core/rules/schema.json once, cached
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

__all__ = [
    "Citation",
    "Enforcement",
    "Rule",
    "load_rule",
    "validate_rule",
    "load_schema",
]


@dataclass(frozen=True)
class Citation:
    source: str
    reference: str


@dataclass(frozen=True)
class Enforcement:
    strategy: str
    tools: Tuple[str, ...]
    notes: str


@dataclass(frozen=True)
class Rule:
    id: str
    number: int
    name: str
    rationale: str
    severity: str
    languages: Tuple[str, ...]
    enforcement: Enforcement
    citations: Tuple[Citation, ...]
    tags: Tuple[str, ...] = ()


# ---------------------------------------------------------------------------
# Schema loading
# ---------------------------------------------------------------------------

# Resolve schema relative to this file so it works regardless of cwd.
# plugin/pow10/rules.py -> repo root is parents[2]
_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCHEMA_PATH = _REPO_ROOT / "core" / "rules" / "schema.json"

_schema_cache: Dict[str, Any] = {}


def load_schema() -> Dict[str, Any]:
    """Load the rule schema once and cache it."""
    if not _schema_cache:
        with _SCHEMA_PATH.open(encoding="utf-8") as f:
            _schema_cache.update(json.load(f))
    return _schema_cache


# ---------------------------------------------------------------------------
# Validator — minimal JSON Schema subset
# ---------------------------------------------------------------------------

# Supported keywords. Any keyword in schema.json that is not in this set is a
# drift bug — the schema author thinks it is being enforced when it is not.
_SUPPORTED_SCHEMA_KEYWORDS = frozenset(
    {
        # Enforced by _validate:
        "type",
        "required",
        "enum",
        "pattern",
        "items",
        "properties",
        "additionalProperties",
        # Metadata-only, safe to ignore:
        "$comment",
        "title",
        "description",
    }
)


class SchemaDriftError(ValueError):
    """Raised when schema.json uses a keyword the validator does not implement."""


def _assert_known_keywords(schema: Dict[str, Any], path: str) -> None:
    """Walk the schema and raise if an unsupported keyword appears."""
    if not isinstance(schema, dict):
        return
    for key in schema:
        if key not in _SUPPORTED_SCHEMA_KEYWORDS:
            raise SchemaDriftError(
                f"{path}: unsupported schema keyword {key!r}; "
                f"validator only implements {sorted(_SUPPORTED_SCHEMA_KEYWORDS)}"
            )
    properties = schema.get("properties", {})
    if isinstance(properties, dict):
        for prop_name, prop_schema in properties.items():
            _assert_known_keywords(prop_schema, f"{path}.properties.{prop_name}")
    items = schema.get("items")
    if items is not None:
        _assert_known_keywords(items, f"{path}.items")


def validate_rule(data: Any) -> List[str]:
    """Validate `data` against core/rules/schema.json. Returns error list."""
    schema = load_schema()
    _assert_known_keywords(schema, "$")
    return _validate(data, schema, "$")


def _validate(data: Any, schema: Dict[str, Any], path: str) -> List[str]:
    errors: List[str] = []
    expected_type = schema.get("type")

    if expected_type == "object":
        if not isinstance(data, dict):
            errors.append(f"{path}: expected object, got {type(data).__name__}")
            return errors
        for key in schema.get("required", []):
            if key not in data:
                errors.append(f"{path}.{key}: required field missing")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in data:
                if key not in properties:
                    errors.append(f"{path}.{key}: unknown property")
        for key, value in data.items():
            if key in properties:
                errors.extend(_validate(value, properties[key], f"{path}.{key}"))

    elif expected_type == "array":
        if not isinstance(data, list):
            errors.append(f"{path}: expected array, got {type(data).__name__}")
            return errors
        item_schema = schema.get("items")
        if item_schema is not None:
            for index, item in enumerate(data):
                errors.extend(_validate(item, item_schema, f"{path}[{index}]"))

    elif expected_type == "string":
        if not isinstance(data, str):
            errors.append(f"{path}: expected string, got {type(data).__name__}")
            return errors
        pattern = schema.get("pattern")
        # Use fullmatch so `$` cannot accept a trailing newline (Python's re.match
        # + "$" diverges from ECMA 262, which JSON Schema draft-7 follows).
        if pattern is not None and re.fullmatch(pattern, data) is None:
            errors.append(f"{path}: does not match pattern {pattern!r}")
        enum = schema.get("enum")
        if enum is not None and data not in enum:
            errors.append(f"{path}: {data!r} is not one of {enum}")

    elif expected_type == "integer":
        # bool is a subclass of int; reject it explicitly.
        if not isinstance(data, int) or isinstance(data, bool):
            errors.append(f"{path}: expected integer, got {type(data).__name__}")
            return errors
        enum = schema.get("enum")
        if enum is not None and data not in enum:
            errors.append(f"{path}: {data!r} is not one of {enum}")

    return errors


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------


class RuleValidationError(ValueError):
    """Raised when a rule file fails schema validation."""


def load_rule(path: Path) -> Rule:
    """Parse a rule JSON file and return an immutable Rule.

    Validates against the schema first; raises RuleValidationError on failure.
    """
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    errors = validate_rule(data)
    if errors:
        raise RuleValidationError(f"{path}: {'; '.join(errors)}")

    enforcement = Enforcement(
        strategy=data["enforcement"]["strategy"],
        tools=tuple(data["enforcement"].get("tools", ())),
        notes=data["enforcement"]["notes"],
    )
    citations = tuple(
        Citation(source=c["source"], reference=c["reference"])
        for c in data["citations"]
    )
    return Rule(
        id=data["id"],
        number=data["number"],
        name=data["name"],
        rationale=data["rationale"],
        severity=data["severity"],
        languages=tuple(data["languages"]),
        enforcement=enforcement,
        citations=citations,
        tags=tuple(data.get("tags", ())),
    )
