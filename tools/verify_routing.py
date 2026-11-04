#!/usr/bin/env python3
"""Validate the cross-skill routing gold set and required negative cases."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTING = ROOT / "evals" / "routing-boundaries.json"
SCIENTIFIC_TRIGGERS = (
    ROOT
    / "plugins"
    / "academic-figure-skills"
    / "skills"
    / "scientific-visualization"
    / "evals"
    / "trigger_cases.json"
)
EXPECTED_ROUTES = {
    "drawio-poster",
    "drawio-academic-skills",
    "scientific-visualization",
    "compose",
    "clarify",
}
MINIMUM_COUNTS = {
    "drawio-poster": 4,
    "drawio-academic-skills": 5,
    "scientific-visualization": 5,
    "compose": 2,
    "clarify": 2,
}


class RoutingError(RuntimeError):
    """Raised when the routing contract is incomplete or inconsistent."""


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_routing() -> dict[str, object]:
    document = load_json(ROUTING)
    if not isinstance(document, dict) or document.get("schema_version") != "1.0":
        raise RoutingError("routing schema_version must be 1.0")
    declared = document.get("routes")
    if not isinstance(declared, list) or set(declared) != EXPECTED_ROUTES:
        raise RoutingError("routing routes must declare the exact supported route set")
    cases = document.get("cases")
    if not isinstance(cases, list):
        raise RoutingError("routing cases must be a list")

    ids: set[str] = set()
    prompts: set[str] = set()
    counts: Counter[str] = Counter()
    for case in cases:
        if not isinstance(case, dict):
            raise RoutingError("every routing case must be an object")
        case_id = case.get("id")
        prompt = case.get("prompt")
        route = case.get("expected_route")
        reason = case.get("reason")
        if not all(isinstance(value, str) and value.strip() for value in (case_id, prompt, reason)):
            raise RoutingError("every routing case requires non-empty id, prompt, and reason")
        if case_id in ids or prompt in prompts:
            raise RoutingError(f"duplicate routing case id or prompt: {case_id}")
        if route not in EXPECTED_ROUTES:
            raise RoutingError(f"unsupported route in {case_id}: {route}")
        ids.add(case_id)
        prompts.add(prompt)
        counts[route] += 1

    for route, minimum in MINIMUM_COUNTS.items():
        if counts[route] < minimum:
            raise RoutingError(f"route {route} needs at least {minimum} cases")

    triggers = load_json(SCIENTIFIC_TRIGGERS)
    if not isinstance(triggers, list):
        raise RoutingError("scientific trigger cases must be a list")
    negative_prompts = {
        item.get("prompt")
        for item in triggers
        if isinstance(item, dict) and item.get("expected") == "do_not_trigger"
    }
    required_negatives = {
        "Design a draw.io architecture diagram for the proposed neural network.",
        "Create a schematic mechanism figure for an IEEE paper.",
    }
    missing = sorted(required_negatives - negative_prompts)
    if missing:
        raise RoutingError(f"scientific-visualization lost drawio negative cases: {missing}")

    return {
        "status": "pass",
        "schema_version": document["schema_version"],
        "cases": len(cases),
        "counts": dict(sorted(counts.items())),
        "scientific_drawio_negative_cases": len(required_negatives),
    }


def main() -> int:
    try:
        print(json.dumps(validate_routing(), indent=2, sort_keys=True))
        return 0
    except (OSError, json.JSONDecodeError, RoutingError) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
