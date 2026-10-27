#!/usr/bin/env python3
"""Offline review contract: verify evidence associations, never semantic truth."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

from _common import CliError, atomic_write_json, emit_json, load_json, sha256_file

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "assets/schemas/figure-review.schema.json"
UNRESOLVED = {"open", "fixed"}


def context_digest(value: dict) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
        separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def file_ref(path: str | None, *, strict: bool = True) -> dict | None:
    if not path:
        if strict:
            raise CliError("missing review input path")
        return None
    try:
        return {"path": str(Path(path).absolute()), "sha256": sha256_file(path)}
    except (CliError, OSError, TypeError, ValueError):
        if strict:
            raise CliError(f"unavailable review input: {path}")
        return {"path": str(path), "sha256": None}


def current_context(document: dict, *, strict: bool = True) -> dict:
    """Exclude QA decisions and the review file to avoid self-referential hashes."""
    render = document.get("render", {})
    qa = document.get("qa", {})
    if not isinstance(render, dict) or not isinstance(qa, dict):
        raise CliError("render and qa must be objects")
    if not isinstance(qa.get("scientific", {}), dict) or not isinstance(qa.get("visual", {}), dict):
        raise CliError("scientific and visual QA must be objects")
    review_path = (qa.get("review") or {}).get("path")
    artifacts = []
    for item in render.get("artifacts", []):
        if not isinstance(item, dict):
            raise CliError("artifact must be an object")
        if review_path and Path(item.get("path", "")).absolute() == Path(review_path).absolute():
            raise CliError("review record cannot also be a rendered artifact")
        if item.get("evidence_label") == "missing-evidence":
            continue
        ref = file_ref(item.get("path"), strict=strict)
        artifacts.append({"role": item.get("role"), "file": ref,
            "text_mode": item.get("text_mode")})
    sources = []
    for item in qa.get("scientific", {}).get("sources", []):
        if not isinstance(item, dict):
            raise CliError("scientific source must be an object")
        if review_path and Path(item["path"]).absolute() == Path(review_path).absolute():
            raise CliError("review record cannot be its own scientific source")
        sources.append({"file": file_ref(item.get("path"), strict=strict), "kind": item.get("kind")})
    return {"figure_id": document.get("figure_id"),
        "contract": copy.deepcopy(document.get("contract", {})),
        "semantic_inventory": copy.deepcopy(document.get("semantic_inventory", {})),
        "canonical_spec": file_ref(render.get("canonical_spec"), strict=strict),
        "artifacts": artifacts, "sources": sources,
        "scientific_basis": qa.get("scientific", {}).get("basis"),
        "visual_artifact": file_ref(qa.get("visual", {}).get("artifact"), strict=strict)}


def review_skeleton(document: dict) -> dict:
    context = current_context(document, strict=False)
    return {"schema_version": "1.0", "figure_id": document.get("figure_id"),
        "scope": "pending", "context": context, "claims": [], "issues": [],
        "readback": {"status": "not_checked", "method": "informed_self_check",
            "reviewer": "", "inputs": [], "artifact": context["visual_artifact"],
            "observations": {"input_output": "", "main_path": "", "line_meanings": "", "detail_mapping": ""},
            "visual_assessment": "", "differences": [],
            "viewing": {"mode": "draft_preview", "width_mm": None, "reason": ""}}}


def _schema_errors(value: Any, schema: dict, path: str = "$") -> list[str]:
    """Bounded validator for the local schema's documented keyword subset."""
    supported = {"$schema", "$id", "title", "description", "type", "const", "enum", "required",
        "properties", "additionalProperties", "items", "minItems", "minLength", "pattern", "exclusiveMinimum"}
    if set(schema) - supported:
        raise CliError(f"unsupported local review schema keywords at {path}")
    types = schema.get("type", [])
    types = [types] if isinstance(types, str) else types
    matches = {"object": isinstance(value, dict), "array": isinstance(value, list),
        "string": isinstance(value, str), "null": value is None, "boolean": isinstance(value, bool),
        "number": isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)}
    if types and not any(matches.get(t, False) for t in types):
        return [f"{path}: expected {types}"]
    errors = []
    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: wrong constant")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: unsupported value")
    if isinstance(value, str):
        if len(value.strip()) < schema.get("minLength", 0):
            errors.append(f"{path}: empty string")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errors.append(f"{path}: invalid pattern")
    if matches["number"] and "exclusiveMinimum" in schema and value <= schema["exclusiveMinimum"]:
        errors.append(f"{path}: number must exceed {schema['exclusiveMinimum']}")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{path}: too few items")
        for index, item in enumerate(value):
            errors.extend(_schema_errors(item, schema.get("items", {}), f"{path}[{index}]"))
    if isinstance(value, dict):
        properties = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}.{key}: required")
        if schema.get("additionalProperties") is False and set(value) - set(properties):
            errors.append(f"{path}: unknown fields {sorted(set(value) - set(properties))}")
        for key in set(value) & set(properties):
            errors.extend(_schema_errors(value[key], properties[key], f"{path}.{key}"))
    return errors


def validate_review(record: Any, document: dict, *, finalizing: bool) -> list[dict]:
    findings = []

    def problem(code, message):
        findings.append({"code": code, "path": "qa.review", "message": message,
            "severity": "error" if finalizing else "warning"})

    errors = _schema_errors(record, load_json(SCHEMA_PATH))
    if errors:
        for error in errors:
            problem("review_schema", error)
        return findings
    if record["figure_id"] != document.get("figure_id"):
        problem("review_figure", "review belongs to another figure")
    try:
        current = current_context(document, strict=finalizing)
    except (CliError, KeyError, TypeError, ValueError) as exc:
        problem("review_inputs", str(exc))
        return findings
    if record["context"] != current:
        problem("review_context_stale", "contract, inventory, sources, spec or exported artifacts changed; re-review affected conclusions")
    if not finalizing:
        return findings
    previous_ref = record.get("previous_review")
    if previous_ref:
        try:
            previous = load_json(previous_ref["path"])
            if previous_ref["sha256"] != sha256_file(previous_ref["path"]) or previous.get("figure_id") != record["figure_id"] or _schema_errors(previous, load_json(SCHEMA_PATH)):
                raise CliError("previous review is changed or invalid")
            issues_now = {x["id"]: x for x in record["issues"]}
            for issue in previous["issues"]:
                retained = issues_now.get(issue["id"])
                if not retained or retained["events"][:len(issue["events"])] != issue["events"] or any(retained[k] != issue[k] for k in ("problem", "evidence", "object_ids", "category")):
                    raise CliError("previous issue history was removed or rewritten")
        except (CliError, OSError, TypeError, KeyError) as exc:
            problem("review_history", str(exc))
    if record["scope"] == "pending":
        problem("review_scope", "declare implementation or conceptual review scope")
    contract = document.get("contract", {})
    if not isinstance(contract.get("caption"), str) or not contract["caption"].strip():
        problem("review_caption", "record the actual caption in contract.caption")
    if not isinstance(document.get("semantic_inventory"), dict) or any(
            not isinstance(document["semantic_inventory"].get(kind), list) or
            any(not isinstance(x, dict) or not isinstance(x.get("id"), str) for x in document["semantic_inventory"][kind])
            for kind in ("nodes", "edges")):
        problem("review_inputs", "invalid semantic inventory")
        return findings
    expected_ids = {x["id"] for kind in ("nodes", "edges") for x in document["semantic_inventory"][kind]}
    covered = set()
    claim_ids = set()
    sources = {x["file"]["path"]: x.get("kind") for x in current["sources"] if x.get("file")}
    kinds = {"code", "configuration", "method", "approved_contract", "data"}
    if not sources or any(kind not in kinds for kind in sources.values()):
        problem("review_source_kind", "label scientific source kinds explicitly")
    if record["scope"] == "implementation" and "code" not in sources.values():
        problem("review_source_kind", "implementation review requires an actual code source")
    for claim in record["claims"]:
        if claim["id"] in claim_ids:
            problem("review_claim_id", "duplicate claim ID")
        claim_ids.add(claim["id"])
        covered.update(claim["object_ids"])
        if claim["status"] != "pass" or any(not claim[k].strip() for k in ("statement", "simplification", "comparison")) or not claim["sources"]:
            problem("review_claim_incomplete", f"claim {claim['id']} needs an explicit source comparison and abstraction decision")
        for source in claim["sources"]:
            if str(Path(source["path"]).absolute()) not in sources or not source["locator"].strip():
                problem("review_claim_source", "claim references an unbound source or empty locator")
    if covered != expected_ids:
        problem("review_claim_coverage", "claims must cover declared node/edge IDs exactly; grouping is allowed")
    readback = record["readback"]
    if readback["status"] != "pass" or not readback["reviewer"].strip() or not readback["visual_assessment"].strip() or any(not s.strip() for s in readback["observations"].values()):
        problem("review_readback", "record actual reading and visual assessment, including inapplicable inset explanations")
    if not {"artifact", "caption", "audience"}.issubset(readback["inputs"]):
        problem("review_readback", "declare the artifact, caption and audience inputs")
    if readback["method"] == "isolated_context" and set(readback["inputs"]) != {"artifact", "caption", "audience"}:
        problem("review_isolation", "isolated reading cannot include design context, code or the claims table")
    artifact = readback["artifact"]
    role = contract.get("delivery_class")
    candidates = [a for a in current["artifacts"] if a["role"] == {"draft-preview": "svg", "raster-publication": "png", "vector-submission": "pdf"}.get(role)
        or (role == "vector-submission" and a["role"] == "svg" and a["text_mode"] == "paths")]
    if not artifact or artifact != current["visual_artifact"] or artifact not in [a["file"] for a in candidates]:
        problem("review_artifact", "read the current delivered primary artifact, not an unrelated preview")
    viewing = readback["viewing"]
    width = contract.get("review_width_mm")
    valid_width = isinstance(width, (int, float)) and not isinstance(width, bool) and math.isfinite(width) and width > 0
    if width is not None and not valid_width:
        problem("review_viewing", "review width must be null or a positive finite number")
    if viewing["mode"] == "intended_size":
        if not valid_width or viewing["width_mm"] != width:
            problem("review_viewing", "viewing width must match contract.review_width_mm")
        scene_path = document.get("qa", {}).get("geometry", {}).get("scene")
        if scene_path and load_json(scene_path).get("width_mm") != width:
            problem("review_viewing", "geometry physical width differs from intended viewing width")
    elif role != "draft-preview" or valid_width or viewing["width_mm"] is not None or not viewing["reason"].strip():
        problem("review_viewing", "only previews without a fixed width may use reasoned draft viewing")
    issues = {}
    active_visual = set()
    for issue in record["issues"]:
        if issue["id"] in issues or not set(issue["object_ids"]).issubset(expected_ids):
            problem("review_issue_identity", "duplicate issue or unknown object ID")
        issues[issue["id"]] = issue
        previous = None
        for event in issue["events"]:
            state = event["state"]
            if previous is None and state != "open":
                problem("review_issue_history", "history starts with an open observation")
            if previous in {"closed", "not_defect"} and state not in {"open", previous}:
                problem("review_issue_history", "reopen a resolved issue before repair")
            previous = state
        last = issue["events"][-1]
        if last["state"] in UNRESOLVED:
            problem("review_issue_unresolved", f"unresolved {issue['category']} issue {issue['id']}")
            if issue["category"] == "visual":
                active_visual.add(issue["id"])
        else:
            refs = last["artifacts"]
            valid_refs = [a["file"] for a in current["artifacts"]]
            if not last["verification"].strip() or not refs or any(ref not in valid_refs for ref in refs) or last["context_sha256"] != context_digest(current):
                problem("review_issue_verification", "resolution needs verification against current context and delivered artifacts")
    visual_items = document.get("qa", {}).get("visual", {}).get("issues", [])
    listed = {item.get("id") for item in visual_items if isinstance(item, dict)}
    if len(listed) != len(visual_items) or listed != active_visual:
        problem("review_active_issues", "qa.visual.issues must match unresolved visual issue IDs in history")
    for diff in readback["differences"]:
        if diff["decision"] == "pending" or not diff["reason"].strip():
            problem("review_difference", "classify and explain every reading discrepancy")
        if diff["decision"] == "defect" and diff["issue_id"] not in issues:
            problem("review_difference", "confirmed reading defect must reference its tracked issue")
    return findings


def verify_review(document: dict, *, finalizing: bool) -> list[dict]:
    severity = "error" if finalizing else "warning"
    def error(code, message):
        return [{"code": code, "path": "qa.review", "message": message, "severity": severity}]
    qa = document.get("qa", {})
    if not isinstance(qa, dict):
        return error("review_inputs", "qa must be an object")
    ref = qa.get("review")
    if not ref:
        return error("review_record_missing", "initialize and complete a current figure.review.json") if finalizing else []
    try:
        if not isinstance(ref, dict) or set(ref) != {"path", "sha256", "schema_version"} or ref["schema_version"] != "1.0":
            return error("review_record_reference", "review reference requires path, sha256 and schema_version 1.0")
        if ref["sha256"] != sha256_file(ref["path"]):
            return error("review_record_stale", "review record hash does not match; inspect changes before rebinding")
        return validate_review(load_json(ref["path"]), document, finalizing=finalizing)
    except (CliError, OSError, KeyError, TypeError, ValueError, AttributeError) as exc:
        return error("review_record_unavailable", str(exc))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("init", "start-round"):
        sub = commands.add_parser(name)
        sub.add_argument("manifest")
        if name == "start-round":
            sub.add_argument("previous_review")
        sub.add_argument("--output", required=True)
    check = commands.add_parser("validate")
    check.add_argument("manifest")
    check.add_argument("--strict", action="store_true")
    try:
        args = parser.parse_args(argv)
        document = load_json(args.manifest)
        if args.command == "validate":
            findings = verify_review(document, finalizing=args.strict or document.get("status") == "accepted")
            emit_json({"findings": findings, "notice": "Checks evidence contracts, not semantic truth."})
            return 2 if any(f["severity"] == "error" for f in findings) else 0
        record = review_skeleton(document)
        if args.command == "start-round":
            previous = load_json(args.previous_review)
            if _schema_errors(previous, load_json(SCHEMA_PATH)) or previous["figure_id"] != record["figure_id"]:
                raise CliError("invalid previous review or different figure")
            record["scope"] = previous["scope"]
            record["claims"] = copy.deepcopy(previous["claims"])
            for claim in record["claims"]:
                claim.update(status="not_checked", comparison="")
            record["issues"] = copy.deepcopy(previous["issues"])
            record["previous_review"] = file_ref(args.previous_review)
        output = Path(args.output).absolute()
        protected = {Path(args.manifest).absolute()}
        for item in record["context"]["artifacts"] + record["context"]["sources"]:
            if item["file"]:
                protected.add(Path(item["file"]["path"]).absolute())
        for ref in (record["context"]["canonical_spec"], record.get("previous_review")):
            if ref:
                protected.add(Path(ref["path"]).absolute())
        if output in protected:
            raise CliError("review output aliases an input")
        atomic_write_json(output, record)
        emit_json({"path": str(output), "sha256": sha256_file(output), "notice": "Pending record only; no review was performed."})
        return 0
    except (CliError, OSError, KeyError, TypeError, ValueError) as exc:
        parser.exit(2, f"error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
