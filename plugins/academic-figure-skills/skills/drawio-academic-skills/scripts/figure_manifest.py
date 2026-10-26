#!/usr/bin/env python3
"""Initialize, build, and validate an overlay-local academic figure manifest."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

from _common import (
    CliError,
    atomic_write_json,
    checked_input_file,
    emit_json,
    load_json,
    sha256_file,
)

SCHEMA_VERSION = "1.0"
FIGURE_TYPES = {"architecture", "workflow", "roadmap"}
DELIVERY_CLASSES = {"raster-publication", "vector-submission", "draft-preview"}
MANIFEST_STATUSES = {"planning", "rendered", "review", "accepted"}
QA_STATUSES = {"pending", "not_checked", "pass", "review", "blocked"}
ARTIFACT_ROLES = {"drawio", "svg", "png", "pdf", "spec", "arch", "preview", "other"}
EVIDENCE_LABELS = {
    "recorded-fixture",
    "command-executed",
    "Desktop-executed",
    "browser-rasterized",
    "model-executed",
    "missing-evidence",
}
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


def manifest_skeleton(figure_id: str, title: str, figure_type: str) -> dict[str, Any]:
    if not SAFE_ID.fullmatch(figure_id):
        raise CliError("figure-id must use letters, digits, dot, underscore, or hyphen")
    if not title.strip():
        raise CliError("title must not be empty")
    if figure_type not in FIGURE_TYPES:
        raise CliError(f"unsupported figure type: {figure_type}")
    return {
        "schema_version": SCHEMA_VERSION,
        "figure_id": figure_id,
        "title": title.strip(),
        "status": "planning",
        "contract": {
            "figure_type": figure_type,
            "delivery_class": "pending",
            "venue": "pending",
            "communication_goal": "pending",
            "intended_claim": "pending",
            "language": "pending",
            "palette": "pending",
            "color_policy": "pending",
            "print_target": "pending",
        },
        "semantic_inventory": {
            "nodes": [],
            "edges": [],
            "abbreviations": [],
            "formulas": [],
            "non_edges": [],
            "forbidden_inferences": [],
            "cross_cutting_regions": [],
        },
        "layout": {
            "candidates": [],
            "selected_id": None,
            "selection_reason": None,
            "wireframe_gate": {
                "status": "pending",
                "review_artifact": None,
                "decision": None,
            },
        },
        "reference_selection": {
            "index_version": "1.0",
            "selected_ids": [],
            "adopted_features": [],
            "rejected_ids": [],
        },
        "render": {
            "canonical_spec": None,
            "artifacts": [],
            "base_cli_commands": [],
        },
        "qa": {
            "deterministic": {"status": "pending", "findings": []},
            "visual": {"status": "not_checked", "artifact": None, "round": 0, "issues": []},
            "publication": {"status": "pending", "checks": []},
            "residual_risks": [],
        },
        "provenance": {
            "sources": [],
            "transformations": [],
            "tool_versions": {},
        },
    }


def _finding(
    findings: list[dict[str, str]],
    code: str,
    path: str,
    message: str,
    *,
    severity: str = "error",
) -> None:
    findings.append(
        {"code": code, "path": path, "message": message, "severity": severity}
    )


def _require_object(
    document: dict[str, Any], key: str, findings: list[dict[str, str]]
) -> dict[str, Any]:
    value = document.get(key)
    if not isinstance(value, dict):
        _finding(findings, "required_object", key, "must be an object")
        return {}
    return value


def _validate_inventory(
    inventory: dict[str, Any],
    findings: list[dict[str, str]],
    *,
    require_boundary_fields: bool,
) -> None:
    nodes = inventory.get("nodes")
    edges = inventory.get("edges")
    if not isinstance(nodes, list):
        _finding(findings, "inventory_nodes", "semantic_inventory.nodes", "must be a list")
        nodes = []
    if not isinstance(edges, list):
        _finding(findings, "inventory_edges", "semantic_inventory.edges", "must be a list")
        edges = []
    node_ids: set[str] = set()
    for index, node in enumerate(nodes):
        path = f"semantic_inventory.nodes[{index}]"
        if not isinstance(node, dict):
            _finding(findings, "node_object", path, "must be an object")
            continue
        node_id = node.get("id")
        if not isinstance(node_id, str) or not SAFE_ID.fullmatch(node_id):
            _finding(findings, "node_id", f"{path}.id", "must be a stable safe ID")
        elif node_id in node_ids:
            _finding(findings, "duplicate_node_id", f"{path}.id", f"duplicate ID {node_id!r}")
        else:
            node_ids.add(node_id)
        if not isinstance(node.get("label"), str) or not node["label"].strip():
            _finding(findings, "node_label", f"{path}.label", "must be non-empty")
        if not isinstance(node.get("role"), str) or not node["role"].strip():
            _finding(findings, "node_role", f"{path}.role", "must be non-empty")

    edge_ids: set[str] = set()
    edge_pairs: set[tuple[str, str]] = set()
    for index, edge in enumerate(edges):
        path = f"semantic_inventory.edges[{index}]"
        if not isinstance(edge, dict):
            _finding(findings, "edge_object", path, "must be an object")
            continue
        edge_id = edge.get("id")
        if not isinstance(edge_id, str) or not SAFE_ID.fullmatch(edge_id):
            _finding(findings, "edge_id", f"{path}.id", "must be a stable safe ID")
        elif edge_id in edge_ids:
            _finding(findings, "duplicate_edge_id", f"{path}.id", f"duplicate ID {edge_id!r}")
        else:
            edge_ids.add(edge_id)
        for endpoint in ("source", "target"):
            value = edge.get(endpoint)
            if value not in node_ids:
                _finding(
                    findings,
                    "unknown_edge_endpoint",
                    f"{path}.{endpoint}",
                    f"must reference a declared node ID; got {value!r}",
                )
        source = edge.get("source")
        target = edge.get("target")
        if isinstance(source, str) and isinstance(target, str):
            edge_pairs.add((source, target))
        if not isinstance(edge.get("relation"), str) or not edge["relation"].strip():
            _finding(findings, "edge_relation", f"{path}.relation", "must be non-empty")
        if not isinstance(edge.get("line_style"), str) or not edge["line_style"].strip():
            _finding(findings, "edge_line_style", f"{path}.line_style", "must be non-empty")

    for key in ("abbreviations", "formulas"):
        if not isinstance(inventory.get(key), list):
            _finding(
                findings,
                "inventory_list",
                f"semantic_inventory.{key}",
                "must be a list",
            )

    boundary_lists: dict[str, list[Any]] = {}
    for key in ("non_edges", "forbidden_inferences", "cross_cutting_regions"):
        value = inventory.get(key)
        if not isinstance(value, list):
            _finding(
                findings,
                "semantic_boundary_fields_required",
                f"semantic_inventory.{key}",
                "must be a list; use an empty list when no boundary applies",
                severity="error" if require_boundary_fields else "warning",
            )
            value = []
        boundary_lists[key] = value

    non_edge_pairs: set[tuple[str, str]] = set()
    for index, non_edge in enumerate(boundary_lists["non_edges"]):
        path = f"semantic_inventory.non_edges[{index}]"
        if not isinstance(non_edge, dict):
            _finding(findings, "non_edge_object", path, "must be an object")
            continue
        source = non_edge.get("source")
        target = non_edge.get("target")
        for endpoint, value in (("source", source), ("target", target)):
            if value not in node_ids:
                _finding(
                    findings,
                    "unknown_non_edge_endpoint",
                    f"{path}.{endpoint}",
                    f"must reference a declared node ID; got {value!r}",
                )
        if not isinstance(non_edge.get("reason"), str) or not non_edge["reason"].strip():
            _finding(findings, "non_edge_reason", f"{path}.reason", "must be non-empty")
        if isinstance(source, str) and isinstance(target, str):
            pair = (source, target)
            if pair in non_edge_pairs:
                _finding(findings, "duplicate_non_edge", path, f"duplicate pair {pair!r}")
            non_edge_pairs.add(pair)
            if pair in edge_pairs:
                _finding(
                    findings,
                    "prohibited_edge_present",
                    path,
                    f"declared non-edge {source!r}->{target!r} also exists in semantic_inventory.edges",
                )

    inference_ids: set[str] = set()
    for index, inference in enumerate(boundary_lists["forbidden_inferences"]):
        path = f"semantic_inventory.forbidden_inferences[{index}]"
        if not isinstance(inference, dict):
            _finding(findings, "forbidden_inference_object", path, "must be an object")
            continue
        inference_id = inference.get("id")
        if not isinstance(inference_id, str) or not SAFE_ID.fullmatch(inference_id):
            _finding(findings, "forbidden_inference_id", f"{path}.id", "must be a stable safe ID")
        elif inference_id in inference_ids:
            _finding(findings, "duplicate_forbidden_inference_id", f"{path}.id", "must be unique")
        else:
            inference_ids.add(inference_id)
        for field in ("statement", "prevention"):
            value = inference.get(field)
            if not isinstance(value, str) or not value.strip():
                _finding(findings, "forbidden_inference_field", f"{path}.{field}", "must be non-empty")

    region_ids: set[str] = set()
    for index, region in enumerate(boundary_lists["cross_cutting_regions"]):
        path = f"semantic_inventory.cross_cutting_regions[{index}]"
        if not isinstance(region, dict):
            _finding(findings, "cross_cutting_region_object", path, "must be an object")
            continue
        region_id = region.get("id")
        if not isinstance(region_id, str) or not SAFE_ID.fullmatch(region_id):
            _finding(findings, "cross_cutting_region_id", f"{path}.id", "must be a stable safe ID")
        elif region_id in region_ids:
            _finding(findings, "duplicate_cross_cutting_region_id", f"{path}.id", "must be unique")
        else:
            region_ids.add(region_id)
        for field in ("label", "semantic_role"):
            value = region.get(field)
            if not isinstance(value, str) or not value.strip():
                _finding(findings, "cross_cutting_region_field", f"{path}.{field}", "must be non-empty")
        members = region.get("member_node_ids")
        if not isinstance(members, list):
            _finding(findings, "cross_cutting_members", f"{path}.member_node_ids", "must be a list")
        else:
            for member_index, member in enumerate(members):
                if member not in node_ids:
                    _finding(
                        findings,
                        "unknown_cross_cutting_member",
                        f"{path}.member_node_ids[{member_index}]",
                        f"must reference a declared node ID; got {member!r}",
                    )
        constraints = region.get("presentation_constraints")
        if not isinstance(constraints, list) or not constraints or any(
            not isinstance(item, str) or not item.strip() for item in constraints
        ):
            _finding(
                findings,
                "cross_cutting_constraints",
                f"{path}.presentation_constraints",
                "must contain at least one non-empty presentation constraint",
            )


def _validate_layout(
    layout: dict[str, Any],
    findings: list[dict[str, str]],
    *,
    require_wireframe_gate: bool,
) -> None:
    candidates = layout.get("candidates")
    if not isinstance(candidates, list):
        _finding(findings, "layout_candidates", "layout.candidates", "must be a list")
        candidates = []
    candidate_ids: set[str] = set()
    for index, candidate in enumerate(candidates):
        path = f"layout.candidates[{index}]"
        if not isinstance(candidate, dict):
            _finding(findings, "layout_candidate", path, "must be an object")
            continue
        candidate_id = candidate.get("id")
        if not isinstance(candidate_id, str) or not SAFE_ID.fullmatch(candidate_id):
            _finding(findings, "layout_candidate_id", f"{path}.id", "must be a safe ID")
        elif candidate_id in candidate_ids:
            _finding(findings, "duplicate_layout_id", f"{path}.id", "must be unique")
        else:
            candidate_ids.add(candidate_id)
    selected = layout.get("selected_id")
    if selected is not None and selected not in candidate_ids:
        _finding(
            findings,
            "unknown_selected_layout",
            "layout.selected_id",
            "must reference one of layout.candidates",
        )
    reason = layout.get("selection_reason")
    if selected and (not isinstance(reason, str) or not reason.strip()):
        _finding(
            findings,
            "layout_selection_reason",
            "layout.selection_reason",
            "must explain why the candidate was selected",
        )
    wireframe_gate = layout.get("wireframe_gate")
    if not isinstance(wireframe_gate, dict):
        _finding(
            findings,
            "wireframe_gate_required",
            "layout.wireframe_gate",
            "must record approved, pending, or not_applicable wireframe review",
            severity="error" if require_wireframe_gate else "warning",
        )
        return
    gate_status = wireframe_gate.get("status")
    if gate_status not in {"pending", "approved", "not_applicable"}:
        _finding(
            findings,
            "wireframe_gate_status",
            "layout.wireframe_gate.status",
            "must be pending, approved, or not_applicable",
        )
    elif require_wireframe_gate and gate_status == "pending":
        _finding(
            findings,
            "wireframe_gate_pending",
            "layout.wireframe_gate.status",
            "must be approved or explicitly not_applicable before strict/final validation",
        )
    decision = wireframe_gate.get("decision")
    if gate_status in {"approved", "not_applicable"} and (
        not isinstance(decision, str) or not decision.strip()
    ):
        _finding(
            findings,
            "wireframe_gate_decision",
            "layout.wireframe_gate.decision",
            "must explain the approval or why a wireframe was not applicable",
        )
    review_artifact = wireframe_gate.get("review_artifact")
    if review_artifact is not None and not isinstance(review_artifact, str):
        _finding(
            findings,
            "wireframe_review_artifact",
            "layout.wireframe_gate.review_artifact",
            "must be a string path or null",
        )


def _validate_render(
    render: dict[str, Any],
    findings: list[dict[str, str]],
    *,
    verify_artifacts: bool,
) -> set[str]:
    artifacts = render.get("artifacts")
    roles: set[str] = set()
    if not isinstance(artifacts, list):
        _finding(findings, "render_artifacts", "render.artifacts", "must be a list")
        return roles
    for index, artifact in enumerate(artifacts):
        path = f"render.artifacts[{index}]"
        if not isinstance(artifact, dict):
            _finding(findings, "artifact_object", path, "must be an object")
            continue
        role = artifact.get("role")
        if role not in ARTIFACT_ROLES:
            _finding(findings, "artifact_role", f"{path}.role", f"unsupported role {role!r}")
        evidence = artifact.get("evidence_label")
        if evidence not in EVIDENCE_LABELS:
            _finding(
                findings,
                "artifact_evidence",
                f"{path}.evidence_label",
                f"unsupported evidence label {evidence!r}",
            )
        artifact_path = artifact.get("path")
        if not isinstance(artifact_path, str) or not artifact_path:
            _finding(findings, "artifact_path", f"{path}.path", "must be non-empty")
            continue
        # A placeholder may be recorded during planning, but cannot satisfy a
        # delivery requirement, even when file verification was not requested.
        if role in ARTIFACT_ROLES and evidence in EVIDENCE_LABELS and evidence != "missing-evidence":
            roles.add(role)
        if verify_artifacts and evidence != "missing-evidence":
            try:
                source = checked_input_file(artifact_path)
            except CliError as exc:
                _finding(findings, "artifact_missing", f"{path}.path", str(exc))
                continue
            expected_hash = artifact.get("sha256")
            if expected_hash and expected_hash != sha256_file(source):
                _finding(findings, "artifact_hash", f"{path}.sha256", "does not match the file")
    if not isinstance(render.get("base_cli_commands"), list):
        _finding(
            findings,
            "base_cli_commands",
            "render.base_cli_commands",
            "must be a list",
        )
    return roles


def validate_manifest(
    document: dict[str, Any], *, strict: bool = False, verify_artifacts: bool = False
) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    allowed_top = {
        "schema_version",
        "figure_id",
        "title",
        "status",
        "contract",
        "semantic_inventory",
        "layout",
        "reference_selection",
        "render",
        "qa",
        "provenance",
    }
    unknown = set(document).difference(allowed_top)
    if unknown:
        _finding(findings, "unknown_top_level", "$", f"unknown fields: {sorted(unknown)}")
    if document.get("schema_version") != SCHEMA_VERSION:
        _finding(findings, "schema_version", "schema_version", "must equal 1.0")
    figure_id = document.get("figure_id")
    if not isinstance(figure_id, str) or not SAFE_ID.fullmatch(figure_id):
        _finding(findings, "figure_id", "figure_id", "must be a stable safe ID")
    if not isinstance(document.get("title"), str) or not document["title"].strip():
        _finding(findings, "title", "title", "must be non-empty")
    status = document.get("status")
    if status not in MANIFEST_STATUSES:
        _finding(findings, "manifest_status", "status", f"unsupported status {status!r}")
    finalizing = status == "accepted" or strict

    contract = _require_object(document, "contract", findings)
    if contract.get("figure_type") not in FIGURE_TYPES:
        _finding(findings, "figure_type", "contract.figure_type", "must use the overlay enum")
    delivery_class = contract.get("delivery_class")
    if delivery_class is None:
        _finding(
            findings,
            "delivery_class_missing",
            "contract.delivery_class",
            "is required for accepted/strict manifests; add it before final delivery",
            severity="error" if status == "accepted" or strict else "warning",
        )
    elif delivery_class != "pending" and delivery_class not in DELIVERY_CLASSES:
        _finding(
            findings,
            "delivery_class",
            "contract.delivery_class",
            "must be raster-publication, vector-submission, draft-preview, or pending",
        )
    for key in (
        "venue",
        "communication_goal",
        "intended_claim",
        "language",
        "palette",
        "color_policy",
        "print_target",
    ):
        if key not in contract:
            _finding(findings, "contract_field", f"contract.{key}", "is required")
    if contract.get("color_policy") not in {
        "pending",
        "color",
        "grayscale",
        "black-white",
        "strict-black-white",
    }:
        _finding(
            findings,
            "color_policy",
            "contract.color_policy",
            "must use the declared color-policy enum",
        )

    inventory = _require_object(document, "semantic_inventory", findings)
    _validate_inventory(
        inventory,
        findings,
        require_boundary_fields=finalizing,
    )
    layout = _require_object(document, "layout", findings)
    _validate_layout(
        layout,
        findings,
        require_wireframe_gate=finalizing,
    )
    references = _require_object(document, "reference_selection", findings)
    selected_references = references.get("selected_ids")
    if not isinstance(selected_references, list):
        _finding(
            findings,
            "reference_selected_ids",
            "reference_selection.selected_ids",
            "must be a list",
        )
    else:
        seen_references: set[str] = set()
        for index, reference_id in enumerate(selected_references):
            path = f"reference_selection.selected_ids[{index}]"
            if not isinstance(reference_id, str) or not SAFE_ID.fullmatch(reference_id):
                _finding(findings, "reference_id", path, "must be a stable safe ID")
            elif reference_id in seen_references:
                _finding(findings, "duplicate_reference_id", path, "must be unique")
            else:
                seen_references.add(reference_id)
    render = _require_object(document, "render", findings)
    roles = _validate_render(render, findings, verify_artifacts=verify_artifacts)
    qa = _require_object(document, "qa", findings)
    for layer in ("deterministic", "visual", "publication"):
        record = qa.get(layer)
        if not isinstance(record, dict) or record.get("status") not in QA_STATUSES:
            _finding(findings, "qa_status", f"qa.{layer}.status", "has an unsupported status")
    if not isinstance(qa.get("residual_risks"), list):
        _finding(findings, "residual_risks", "qa.residual_risks", "must be a list")
    provenance = _require_object(document, "provenance", findings)
    for key in ("sources", "transformations"):
        if not isinstance(provenance.get(key), list):
            _finding(findings, "provenance_list", f"provenance.{key}", "must be a list")
    if not isinstance(provenance.get("tool_versions"), dict):
        _finding(
            findings,
            "tool_versions",
            "provenance.tool_versions",
            "must be an object",
        )

    if finalizing:
        if not layout.get("selected_id"):
            _finding(findings, "selected_layout_required", "layout.selected_id", "is required")
        if not inventory.get("nodes"):
            _finding(findings, "semantic_nodes_required", "semantic_inventory.nodes", "must not be empty")
        if "drawio" not in roles or not roles.intersection({"svg", "png", "pdf"}):
            _finding(
                findings,
                "final_artifacts_required",
                "render.artifacts",
                "must include drawio and at least one inspectable SVG/PNG/PDF",
            )
        artifacts = render.get("artifacts") if isinstance(render.get("artifacts"), list) else []
        if delivery_class == "raster-publication" and "png" not in roles:
            _finding(
                findings,
                "delivery_artifact",
                "render.artifacts",
                "raster-publication requires a PNG artifact",
            )
        if delivery_class == "vector-submission":
            has_path_svg = any(
                isinstance(item, dict)
                and item.get("role") == "svg"
                and item.get("text_mode") == "paths"
                and item.get("evidence_label") in EVIDENCE_LABELS - {"missing-evidence"}
                for item in artifacts
            )
            if "pdf" not in roles and not has_path_svg:
                _finding(
                    findings,
                    "delivery_artifact",
                    "render.artifacts",
                    "vector-submission requires PDF or SVG explicitly marked text_mode=paths",
                )
        if delivery_class == "draft-preview" and "svg" not in roles:
            _finding(
                findings,
                "delivery_artifact",
                "render.artifacts",
                "draft-preview requires an SVG preview artifact",
            )
        for layer in ("deterministic", "visual", "publication"):
            layer_status = (qa.get(layer) or {}).get("status")
            if layer_status in {"pending", "not_checked", "blocked", None}:
                _finding(
                    findings,
                    "qa_incomplete",
                    f"qa.{layer}.status",
                    f"cannot be {layer_status!r} for accepted/strict validation",
                )
        for key, value in contract.items():
            if value == "pending":
                _finding(
                    findings,
                    "contract_pending",
                    f"contract.{key}",
                    "must be resolved or explicitly marked not_applicable",
                )

    errors = sum(item["severity"] == "error" for item in findings)
    warnings = sum(item["severity"] == "warning" for item in findings)
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "fail" if errors else ("review" if warnings else "pass"),
        "summary": {"errors": errors, "warnings": warnings},
        "findings": findings,
        "notice": (
            "Manifest validation checks structure and recorded evidence only. It does "
            "not establish scientific correctness, copyright safety, or venue compliance."
        ),
    }


def hydrate_artifacts(document: dict[str, Any]) -> dict[str, Any]:
    render = document.get("render")
    if not isinstance(render, dict) or not isinstance(render.get("artifacts"), list):
        raise CliError("render.artifacts must be a list before build")
    for artifact in render["artifacts"]:
        if not isinstance(artifact, dict):
            raise CliError("every artifact must be an object")
        if artifact.get("evidence_label") == "missing-evidence":
            artifact["sha256"] = None
            artifact["size_bytes"] = None
            continue
        path = checked_input_file(artifact.get("path", ""))
        artifact["sha256"] = sha256_file(path)
        artifact["size_bytes"] = path.stat().st_size
    return document


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build and validate academic figure manifests.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    initialize = subparsers.add_parser("init", help="write a planning manifest skeleton")
    initialize.add_argument("--figure-id", required=True)
    initialize.add_argument("--title", required=True)
    initialize.add_argument("--figure-type", required=True, choices=tuple(sorted(FIGURE_TYPES)))
    initialize.add_argument("--output", required=True)
    initialize.add_argument("--force", action="store_true")

    validate = subparsers.add_parser("validate", help="validate a manifest")
    validate.add_argument("input")
    validate.add_argument("--strict", action="store_true")
    validate.add_argument("--verify-artifacts", action="store_true")

    build = subparsers.add_parser("build", help="hash artifacts and write canonical JSON")
    build.add_argument("input")
    build.add_argument("--output", required=True)
    build.add_argument("--strict", action="store_true")
    build.add_argument("--force", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
        if args.command == "init":
            document = manifest_skeleton(args.figure_id, args.title, args.figure_type)
            atomic_write_json(args.output, document, force=args.force)
            emit_json({"status": "written", "path": str(Path(args.output).resolve())})
            return 0
        document = load_json(args.input)
        if args.command == "validate":
            report = validate_manifest(
                document,
                strict=args.strict,
                verify_artifacts=args.verify_artifacts,
            )
            emit_json(report)
            return 0 if report["status"] != "fail" else 2
        document = hydrate_artifacts(document)
        report = validate_manifest(document, strict=args.strict, verify_artifacts=True)
        if report["status"] == "fail":
            emit_json(report)
            return 2
        atomic_write_json(args.output, document, force=args.force)
        emit_json(
            {
                "status": "written",
                "path": str(Path(args.output).resolve()),
                "validation": report,
            }
        )
        return 0
    except CliError as exc:
        parser.exit(2, f"error: {exc}\n")


if __name__ == "__main__":
    sys.exit(main())
