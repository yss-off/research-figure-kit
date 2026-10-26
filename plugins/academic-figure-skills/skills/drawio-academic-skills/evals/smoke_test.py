#!/usr/bin/env python3
"""Offline regression checks for overlay-local planning and evidence helpers."""

from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from _common import CliError, atomic_write_json, sha256_file  # noqa: E402
from test_audit_connectors import ConnectorAuditTests  # noqa: E402,F401
from figure_manifest import (  # noqa: E402
    hydrate_artifacts,
    manifest_skeleton,
    validate_manifest,
)
from layout_candidates import build_candidates  # noqa: E402
from reference_index import load_index, query_index  # noqa: E402


def load_fixture(name: str) -> dict:
    return json.loads((Path(__file__).parent / name).read_text(encoding="utf-8"))


def accepted_manifest(drawio: Path, svg: Path) -> dict:
    document = manifest_skeleton("figure-smoke", "Smoke figure", "architecture")
    document["status"] = "accepted"
    document["contract"].update(
        {
            "venue": "test-fixture",
            "delivery_class": "draft-preview",
            "communication_goal": "exercise the evidence contract",
            "intended_claim": "structural smoke test only",
            "language": "en",
            "palette": "ieee-bw",
            "color_policy": "strict-black-white",
            "print_target": "not_applicable",
        }
    )
    document["semantic_inventory"].update(
        {
            "nodes": [
                {"id": "input", "label": "Input", "role": "source"},
                {"id": "output", "label": "Output", "role": "sink"},
                {"id": "support", "label": "Shared support", "role": "cross-cutting support"},
            ],
            "edges": [
                {
                    "id": "flow",
                    "source": "input",
                    "target": "output",
                    "relation": "produces",
                    "line_style": "solid",
                }
            ],
            "non_edges": [
                {
                    "source": "support",
                    "target": "output",
                    "reason": "The support band must not read as a process input.",
                }
            ],
            "forbidden_inferences": [
                {
                    "id": "support-controls-output",
                    "statement": "Shared support directly controls the output stage.",
                    "prevention": "Keep the support region unnumbered and outside the process arrows.",
                }
            ],
            "cross_cutting_regions": [
                {
                    "id": "support-band",
                    "label": "Shared support",
                    "semantic_role": "non-sequential engineering support",
                    "member_node_ids": ["support"],
                    "presentation_constraints": [
                        "Must not be numbered as a process lane.",
                        "Must not connect to the main flow without an explicit relation.",
                    ],
                }
            ],
        }
    )
    document["layout"] = {
        "candidates": [
            {"id": "architecture-layered"},
            {"id": "architecture-modular-grid"},
        ],
        "selected_id": "architecture-layered",
        "selection_reason": "The confirmed relation is a single left-to-right path.",
        "wireframe_gate": {
            "status": "approved",
            "review_artifact": None,
            "decision": "A text wireframe confirmed one process path and one non-process support band.",
        },
    }
    document["reference_selection"]["selected_ids"] = ["example-system-architecture"]
    document["render"].update(
        {
            "canonical_spec": "fixture.yaml",
            "artifacts": [
                {
                    "role": "drawio",
                    "path": str(drawio),
                    "evidence_label": "command-executed",
                },
                {
                    "role": "svg",
                    "path": str(svg),
                    "evidence_label": "command-executed",
                },
            ],
            "base_cli_commands": ["fixture command"],
        }
    )
    document["qa"] = {
        "deterministic": {"status": "pass", "findings": []},
        "visual": {"status": "pass", "artifact": str(svg), "round": 1, "issues": []},
        "publication": {"status": "pass", "checks": []},
        "residual_risks": ["This is a structural fixture, not venue evidence."],
    }
    return document


class ReferenceIndexTests(unittest.TestCase):
    def test_index_is_local_unique_and_queryable(self) -> None:
        index = load_index()
        self.assertEqual(10, len(index["entries"]))
        self.assertEqual(10, len({item["id"] for item in index["entries"]}))
        result = query_index(figure_type="architecture", features=["deep-learning"])
        self.assertEqual(
            ["example-yolo-model-architecture", "template-neural-network-compact"],
            [item["id"] for item in result["matches"]],
        )
        self.assertTrue(all(item["license"] == "MIT" for item in index["entries"]))


class LayoutCandidateTests(unittest.TestCase):
    def test_all_layout_fixtures(self) -> None:
        fixture = load_fixture("layout-choice-cases.json")
        self.assertEqual(12, len(fixture["cases"]))
        for case in fixture["cases"]:
            with self.subTest(case=case["id"]):
                result = build_candidates(
                    case["figure_type"],
                    case["sections"],
                    has_feedback=case.get("has_feedback", False),
                    secondary_axis=case.get("secondary_axis", False),
                    count=case.get("count", 3),
                )
                candidates = result["candidates"]
                self.assertIn(len(candidates), {2, 3})
                self.assertEqual(len(candidates), len({item["id"] for item in candidates}))
                self.assertTrue(
                    all(item["section_order"] == case["sections"] for item in candidates)
                )
                self.assertTrue(
                    all(item["scientific_content_status"] == "unchanged" for item in candidates)
                )
                if "expected_candidate_ids" in case:
                    self.assertEqual(
                        case["expected_candidate_ids"],
                        [item["id"] for item in candidates],
                    )
                if "expected_count" in case:
                    self.assertEqual(case["expected_count"], len(candidates))
                if "expected_edge_phrase" in case:
                    self.assertTrue(
                        all(
                            case["expected_edge_phrase"] in item["edge_strategy"]
                            for item in candidates
                        )
                    )

    def test_invalid_candidate_count_is_rejected(self) -> None:
        with self.assertRaises(CliError):
            build_candidates("workflow", ["A", "B"], count=1)


class ManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.work = Path(self.temporary.name)
        self.drawio = self.work / "figure.drawio"
        self.svg = self.work / "figure.svg"
        self.drawio.write_text("<mxfile/>", encoding="utf-8")
        self.svg.write_text("<svg xmlns='http://www.w3.org/2000/svg'/>", encoding="utf-8")
        self.valid = hydrate_artifacts(accepted_manifest(self.drawio, self.svg))

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_accepted_manifest_and_artifact_hashes(self) -> None:
        report = validate_manifest(self.valid, strict=True, verify_artifacts=True)
        self.assertEqual("pass", report["status"])
        for artifact in self.valid["render"]["artifacts"]:
            self.assertEqual(64, len(artifact["sha256"]))
            self.assertGreater(artifact["size_bytes"], 0)

    def test_missing_evidence_cannot_satisfy_final_delivery(self) -> None:
        for delivery_class, role in (("draft-preview", "svg"),
                                     ("raster-publication", "png"),
                                     ("vector-submission", "pdf"),
                                     ("vector-submission", "svg")):
            for status in ("accepted", "rendered"):
                for verify in (False, True):
                    with self.subTest(delivery_class=delivery_class, role=role,
                                      status=status, verify=verify):
                        document = copy.deepcopy(self.valid)
                        document["status"] = status
                        document["contract"]["delivery_class"] = delivery_class
                        document["render"]["artifacts"][1] = {
                            "role": role, "path": str(self.work / "absent"),
                            "text_mode": "paths", "evidence_label": "missing-evidence",
                        }
                        report = validate_manifest(document, strict=True, verify_artifacts=verify)
                        self.assertEqual("fail", report["status"])
                        self.assertIn("delivery_artifact", {f["code"] for f in report["findings"]})
        document = copy.deepcopy(self.valid)
        document["render"]["artifacts"][0]["evidence_label"] = "missing-evidence"
        self.assertEqual("fail", validate_manifest(document)["status"])

    def test_planning_manifest_can_record_missing_artifacts(self) -> None:
        document = manifest_skeleton("planning", "Unrendered figure", "architecture")
        document["render"]["artifacts"] = [{
            "role": "svg", "path": str(self.work / "absent.svg"),
            "evidence_label": "missing-evidence",
        }]
        self.assertEqual("pass", validate_manifest(document, verify_artifacts=True)["status"])

    def test_known_bad_manifest_cases(self) -> None:
        fixture = load_fixture("manifest-known-bad.json")
        self.assertEqual(15, len(fixture["cases"]))
        for case in fixture["cases"]:
            with self.subTest(case=case["id"]):
                document = copy.deepcopy(self.valid)
                mutation = case["mutation"]
                if mutation == "duplicate_node":
                    document["semantic_inventory"]["nodes"].append(
                        copy.deepcopy(document["semantic_inventory"]["nodes"][0])
                    )
                elif mutation == "unknown_edge_source":
                    document["semantic_inventory"]["edges"][0]["source"] = "missing"
                elif mutation == "unknown_selected_layout":
                    document["layout"]["selected_id"] = "not-a-candidate"
                elif mutation == "empty_selection_reason":
                    document["layout"]["selection_reason"] = "  "
                elif mutation == "duplicate_reference":
                    document["reference_selection"]["selected_ids"] *= 2
                elif mutation == "unsafe_reference_id":
                    document["reference_selection"]["selected_ids"] = ["../unsafe"]
                elif mutation == "missing_final_artifact":
                    document["render"]["artifacts"] = []
                elif mutation == "qa_pending":
                    document["qa"]["visual"]["status"] = "pending"
                elif mutation == "contract_pending":
                    document["contract"]["venue"] = "pending"
                elif mutation == "artifact_hash_mismatch":
                    document["render"]["artifacts"][0]["sha256"] = "0" * 64
                elif mutation == "unknown_non_edge_endpoint":
                    document["semantic_inventory"]["non_edges"][0]["source"] = "missing"
                elif mutation == "prohibited_edge_present":
                    document["semantic_inventory"]["edges"].append(
                        {
                            "id": "forbidden-flow",
                            "source": "support",
                            "target": "output",
                            "relation": "incorrectly controls",
                            "line_style": "solid",
                        }
                    )
                elif mutation == "duplicate_forbidden_inference":
                    document["semantic_inventory"]["forbidden_inferences"] *= 2
                elif mutation == "unknown_cross_cutting_member":
                    document["semantic_inventory"]["cross_cutting_regions"][0][
                        "member_node_ids"
                    ] = ["missing"]
                elif mutation == "wireframe_gate_pending":
                    document["layout"]["wireframe_gate"] = {
                        "status": "pending",
                        "review_artifact": None,
                        "decision": None,
                    }
                else:
                    self.fail(f"unknown fixture mutation: {mutation}")
                report = validate_manifest(document, strict=True, verify_artifacts=True)
                codes = {item["code"] for item in report["findings"]}
                self.assertIn(case["expected_code"], codes)
                self.assertEqual("fail", report["status"])

    def test_atomic_write_refuses_implicit_overwrite(self) -> None:
        output = self.work / "manifest.json"
        atomic_write_json(output, self.valid)
        with self.assertRaises(CliError):
            atomic_write_json(output, self.valid)
        atomic_write_json(output, self.valid, force=True)
        loaded = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(sha256_file(self.svg), loaded["render"]["artifacts"][1]["sha256"])

    def test_delivery_class_requires_matching_artifact(self) -> None:
        cases = (
            ("raster-publication", "PNG artifact"),
            ("vector-submission", "PDF or SVG"),
        )
        for delivery_class, expected in cases:
            with self.subTest(delivery_class=delivery_class):
                document = copy.deepcopy(self.valid)
                document["contract"]["delivery_class"] = delivery_class
                report = validate_manifest(document, strict=True, verify_artifacts=True)
                finding = next(
                    item for item in report["findings"] if item["code"] == "delivery_artifact"
                )
                self.assertIn(expected, finding["message"])

    def test_delivery_class_accepts_matching_artifact(self) -> None:
        raster = copy.deepcopy(self.valid)
        png = self.work / "figure.png"
        png.write_bytes(b"png regression fixture")
        raster["contract"]["delivery_class"] = "raster-publication"
        raster["render"]["artifacts"].append(
            {
                "role": "png",
                "path": str(png),
                "evidence_label": "recorded-fixture",
            }
        )
        raster = hydrate_artifacts(raster)
        self.assertEqual(
            "pass",
            validate_manifest(raster, strict=True, verify_artifacts=True)["status"],
        )

        vector = copy.deepcopy(self.valid)
        vector["contract"]["delivery_class"] = "vector-submission"
        vector["render"]["artifacts"][1]["text_mode"] = "paths"
        self.assertEqual(
            "pass",
            validate_manifest(vector, strict=True, verify_artifacts=True)["status"],
        )

    def test_legacy_planning_manifest_gets_migration_warning(self) -> None:
        legacy = manifest_skeleton("legacy", "Legacy planning manifest", "workflow")
        del legacy["contract"]["delivery_class"]
        report = validate_manifest(legacy)
        self.assertEqual("review", report["status"])
        self.assertIn(
            "delivery_class_missing",
            {item["code"] for item in report["findings"]},
        )
        strict_report = validate_manifest(legacy, strict=True)
        self.assertEqual("fail", strict_report["status"])


class AcceptanceInventoryTests(unittest.TestCase):
    def test_acceptance_inventory_has_unique_checks(self) -> None:
        checks = load_fixture("acceptance.json")["checks"]
        self.assertEqual(9, len(checks))
        self.assertEqual(len(checks), len({item["id"] for item in checks}))


if __name__ == "__main__":
    unittest.main(verbosity=2)
