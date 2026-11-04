"""Contract regressions, not a benchmark of reviewer semantic accuracy."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _common import sha256_file
from figure_review import context_digest, current_context, review_skeleton, validate_review


def completed_review(document):
    """Explicit synthetic reviewer evidence; never used as a production auto-pass."""
    record = review_skeleton(document)
    record["scope"] = "conceptual"
    source = document["qa"]["scientific"]["sources"][0]["path"]
    ids = [x["id"] for kind in ("nodes", "edges") for x in document["semantic_inventory"][kind]]
    record["claims"] = [{"id": "contract-claim", "object_ids": ids,
        "statement": "Anonymous fixture follows its explicit contract.",
        "sources": [{"path": source, "locator": "Whole fixture contract"}],
        "simplification": "No additional empirical or implementation claim.",
        "status": "pass", "comparison": "Synthetic fixture comparison only."}]
    record["readback"].update(status="pass", method="informed_self_check", reviewer="fixture",
        inputs=["artifact", "caption", "audience", "design_context"],
        observations={"input_output": "Input to output", "main_path": "Directed flow",
            "line_meanings": "Solid operational flow", "detail_mapping": "No inset"},
        visual_assessment="Synthetic intended-size viewing record; no quality claim.")
    width = document["contract"].get("review_width_mm")
    record["readback"]["viewing"] = {"mode": "intended_size" if width else "draft_preview",
        "width_mm": width, "reason": "Publication target not fixed" if not width else "Declared width"}
    return record


def bind_review(document, record, path):
    path.write_text(json.dumps(record), encoding="utf-8")
    document["qa"]["review"] = {"path": str(path), "sha256": sha256_file(path), "schema_version": "1.0"}


class FigureReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.work = Path(self.tmp.name)
        # Import lazily: smoke imports this class before defining its fixture.
        from smoke_test import accepted_manifest
        self.drawio = self.work / "figure.drawio"
        self.svg = self.work / "figure.svg"
        self.drawio.write_text("<mxfile/>")
        self.svg.write_text("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 140 100'><rect id='input' x='0' y='0' width='20' height='20'/><rect id='output' x='80' y='0' width='20' height='20'/><rect id='support' x='0' y='60' width='100' height='20'/><line id='flow' x1='20' y1='10' x2='80' y2='10'/></svg>")
        self.doc = accepted_manifest(self.drawio, self.svg)
        self.record = completed_review(self.doc)

    def tearDown(self):
        self.tmp.cleanup()

    def codes(self, record=None, document=None, finalizing=True):
        return {f["code"] for f in validate_review(record if record is not None else self.record,
            document if document is not None else self.doc, finalizing=finalizing)}

    def test_conceptual_contract_without_implementation_is_valid(self):
        self.assertEqual(set(), self.codes())

    def test_initializer_never_attests_a_review(self):
        record = review_skeleton(self.doc)
        self.assertEqual("not_checked", record["readback"]["status"])
        self.assertNotEqual(set(), self.codes(record))

    def test_malformed_record_is_a_finding_not_a_crash(self):
        for value in (None, [], {"schema_version": "1.0"}, {**self.record, "issues": [None]}):
            self.assertIn("review_schema", self.codes(value if value is not None else []))

    def test_record_hash_and_final_checks_cannot_be_bypassed(self):
        from figure_manifest import validate_manifest, hydrate_artifacts
        d = hydrate_artifacts(copy.deepcopy(self.doc))
        for mutation, expected in (("missing", "review_record_missing"), ("hash", "review_record_stale")):
            altered = copy.deepcopy(d)
            if mutation == "missing": altered["qa"].pop("review")
            else: altered["qa"]["review"]["sha256"] = "0" * 64
            result = validate_manifest(altered, verify_artifacts=False)
            self.assertEqual("fail", result["status"])
            self.assertIn(expected, {x["code"] for x in result["findings"]})
        r = copy.deepcopy(self.record); r["claims"][0]["status"] = "not_checked"
        bind_review(d, r, self.work / "incomplete.review.json")
        self.assertEqual("fail", validate_manifest(d, strict=True)["status"])

    def test_rebinding_record_hash_does_not_refresh_old_context(self):
        from figure_manifest import validate_manifest
        d = copy.deepcopy(self.doc); d["contract"]["caption"] = "Changed meaning"
        bind_review(d, self.record, self.work / "rehashed.review.json")
        self.assertIn("review_context_stale", {x["code"] for x in validate_manifest(d)["findings"]})

    def test_history_link_detects_deleted_or_rewritten_events(self):
        previous = copy.deepcopy(self.record); previous["issues"] = [self.issue()]
        p = self.work / "previous.review.json"; p.write_text(json.dumps(previous))
        current = copy.deepcopy(self.record)
        current["previous_review"] = {"path": str(p), "sha256": sha256_file(p)}
        self.assertIn("review_history", self.codes(current))
        current["issues"] = copy.deepcopy(previous["issues"])
        current["issues"][0]["events"][0]["decision"] = "Rewritten"
        self.assertIn("review_history", self.codes(current))

    def test_start_round_retains_history_and_resets_attestations(self):
        previous = copy.deepcopy(self.record); previous["issues"] = [self.issue()]
        p = self.work / "prior.review.json"; p.write_text(json.dumps(previous))
        manifest = self.work / "figure.manifest.json"; manifest.write_text(json.dumps(self.doc))
        output = self.work / "next.review.json"
        result = subprocess.run([sys.executable, str(ROOT / "scripts/figure_review.py"), "start-round", str(manifest), str(p), "--output", str(output)], capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stderr)
        current = json.loads(output.read_text())
        self.assertEqual(previous["issues"], current["issues"])
        self.assertEqual("not_checked", current["readback"]["status"])
        self.assertEqual("not_checked", current["claims"][0]["status"])
        self.assertTrue(current["previous_review"]["sha256"])

    def test_missing_claim_and_unknown_object_are_rejected(self):
        for ids in (["input"], ["input", "output", "support", "flow", "invented"]):
            r = copy.deepcopy(self.record); r["claims"][0]["object_ids"] = ids
            self.assertIn("review_claim_coverage", self.codes(r))

    def test_implementation_claim_requires_implementation_source(self):
        r = copy.deepcopy(self.record); r["scope"] = "implementation"
        self.assertIn("review_source_kind", self.codes(r))

    def test_each_context_input_invalidates_old_record(self):
        for field in ("caption", "review_width_mm", "intended_claim"):
            d = copy.deepcopy(self.doc); d["contract"][field] = 99 if field == "review_width_mm" else "changed"
            self.assertIn("review_context_stale", self.codes(document=d))
        d = copy.deepcopy(self.doc); d["semantic_inventory"]["edges"][0]["target"] = "support"
        self.assertIn("review_context_stale", self.codes(document=d))
        for file in (self.svg, Path(self.doc["render"]["canonical_spec"]), Path(self.doc["qa"]["scientific"]["sources"][0]["path"])):
            old = file.read_bytes(); file.write_bytes(old + b"\nchanged")
            self.assertIn("review_context_stale", self.codes())
            file.write_bytes(old)

    def test_arbitrary_reviewed_artifact_is_rejected(self):
        extra = self.work / "unrelated.svg"; extra.write_text("<svg/>")
        d = copy.deepcopy(self.doc); d["qa"]["visual"]["artifact"] = str(extra)
        r = completed_review(d)
        self.assertIn("review_artifact", self.codes(r, d))

    def issue(self, state="open"):
        return {"id": "arrow", "object_ids": ["flow"], "category": "visual",
            "problem": "Arrow label crossed text", "evidence": "Observed at flow endpoint",
            "events": [{"state": "open", "decision": "Repair routing", "verification": "",
                "context_sha256": context_digest(current_context(self.doc)), "artifacts": []}]}

    def test_hidden_unresolved_issue_and_fixed_without_verification_block(self):
        r = copy.deepcopy(self.record); issue = self.issue(); r["issues"].append(issue)
        self.assertIn("review_active_issues", self.codes(r))
        self.assertIn("review_issue_unresolved", self.codes(r))
        issue["events"].append({**issue["events"][0], "state": "fixed"})
        self.assertIn("review_issue_unresolved", self.codes(r))

    def test_closed_issue_retains_history_and_can_reopen(self):
        r = copy.deepcopy(self.record); issue = self.issue(); r["issues"] = [issue]
        proof = {"path": str(self.svg), "sha256": sha256_file(self.svg)}
        issue["events"].append({**issue["events"][0], "state": "closed",
            "decision": "Adjusted arrow route", "verification": "Rechecked whole route and initialization relation", "artifacts": [proof]})
        self.assertEqual(set(), self.codes(r))
        issue["events"][-1]["verification"] = ""
        self.assertIn("review_issue_verification", self.codes(r))
        issue["events"][-1]["verification"] = "Rechecked"
        issue["events"].append({**issue["events"][0], "state": "open", "decision": "Regression after re-export"})
        self.assertIn("review_issue_unresolved", self.codes(r))
        self.assertEqual(3, len(issue["events"]))

    def test_blind_reading_cannot_declare_design_context(self):
        r = copy.deepcopy(self.record); r["readback"]["method"] = "isolated_context"
        self.assertIn("review_isolation", self.codes(r))
        r["readback"]["inputs"] = ["artifact", "caption", "audience"]
        self.assertEqual(set(), self.codes(r))

    def test_pending_difference_blocks_and_abstraction_needs_reason(self):
        r = copy.deepcopy(self.record)
        r["readback"]["differences"] = [{"observation": "Projection not drawn", "decision": "pending", "reason": "", "issue_id": None}]
        self.assertIn("review_difference", self.codes(r))
        r["readback"]["differences"][0].update(decision="allowed_abstraction", reason="Caption explicitly excludes decoder details")
        self.assertEqual(set(), self.codes(r))

    def test_self_consistent_semantic_error_is_not_detected_by_contract(self):
        r = copy.deepcopy(self.record); r["claims"][0]["statement"] = "Scientifically incorrect but structurally consistent assertion"
        self.assertEqual(set(), self.codes(r))

    def test_migration_preserves_input_and_does_not_approve(self):
        d = copy.deepcopy(self.doc); d["schema_version"] = "1.0"
        d["qa"]["visual"]["issues"] = [{"problem": "Legacy unresolved visual issue"}]
        source = self.work / "legacy.json"; source.write_text(json.dumps(d))
        before = source.read_bytes(); output = self.work / "migrated.json"
        command = [sys.executable, str(ROOT / "scripts/figure_manifest.py"), "migrate", str(source), "--output", str(output)]
        result = subprocess.run(command, text=True, capture_output=True)
        self.assertEqual(0, result.returncode, result.stderr)
        migrated = json.loads(output.read_text())
        self.assertEqual(before, source.read_bytes())
        self.assertEqual("1.1", migrated["schema_version"])
        self.assertEqual("review", migrated["status"])
        self.assertEqual("not_checked", migrated["qa"]["visual"]["status"])
        self.assertEqual("not_checked", migrated["qa"]["scientific"]["status"])
        self.assertTrue(migrated["qa"]["visual"]["issues"])
        self.assertNotEqual(0, subprocess.run(command, capture_output=True).returncode)


if __name__ == "__main__":
    unittest.main()
