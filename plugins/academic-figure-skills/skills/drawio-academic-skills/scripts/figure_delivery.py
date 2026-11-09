#!/usr/bin/env python3
"""Report current delivery evidence and revision impact; never certify meaning."""
from __future__ import annotations

import argparse
from pathlib import Path

from _common import CliError, atomic_write_json, emit_json, load_json, sha256_file
from figure_manifest import evaluate_manifest
from figure_review import revision_impact


def delivery_report(document: dict) -> dict:
    """Always request strict replay, even for a diagnostic draft."""
    evaluation = None
    try:
        evaluation = evaluate_manifest(document, strict=True, verify_artifacts=True)
        validation = evaluation.validation
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        validation = {"status": "fail", "findings": [{"code": "delivery_inputs_invalid", "path": "$", "severity": "error", "message": str(exc)}]}
    findings = validation["findings"]
    qa = document.get("qa") if isinstance(document.get("qa"), dict) else {}
    def record(name):
        return qa.get(name) if isinstance(qa.get(name), dict) else {}
    def layer(name, scope, present, declared=None):
        relevant = evaluation.findings_by_layer[name] if evaluation else findings
        complete = evaluation is not None and evaluation.checks[name].complete
        state = ("not_checked" if not present else "review" if relevant or declared not in (None, "pass")
                 else "evidence_checked" if complete else "not_checked")
        return {"status": state, "recorded_status": declared, "scope": scope, "findings": relevant}
    layers = {
        "structure_export": layer("structure_export", "Manifest structure and current delivered file hashes; not renderer parity.",
            bool(document.get("render")), record("deterministic").get("status", "not_checked")),
        "geometry": layer("geometry", "Replay of supported SVG geometry only; not route quality or aesthetic judgment.",
            bool(record("geometry"))),
        "scientific": layer("scientific", "Current source/claim/review evidence associations; not independent scientific truth.",
            bool(record("scientific")) and bool(record("review")), record("scientific").get("status", "not_checked")),
        "readability": layer("readability", "Recorded actual-artifact reading, visual assessment and issue history; reviewer effectiveness is unmeasured.",
            bool(record("review")), record("visual").get("status", "not_checked")),
        "publication": layer("publication", "Recorded checks for the selected delivery class; not publisher acceptance or copyright clearance.",
            isinstance(record("publication").get("checks"), list) and bool(record("publication")["checks"]),
            record("publication").get("status", "not_checked")),
    }
    # Strict validation owns completeness; layers explain its evidence findings.
    complete = validation["status"] == "pass"
    return {"schema_version": "1.0", "figure_id": document.get("figure_id"),
        "delivery_class": (document.get("contract") or {}).get("delivery_class") if isinstance(document.get("contract"), dict) else None,
        "status": "evidence_complete" if complete else "needs_review",
        "validation_status": validation["status"], "layers": layers, "findings": findings,
        "residual_risks": qa.get("residual_risks", []),
        "notice": "Evidence completeness is not visual/scientific certification or author approval. No image inspection was performed by this command. Missing checks remain missing; source files are never modified."}


def protected_paths(value):
    """Protect referenced inputs, including nested geometry and history files."""
    result = set()
    if isinstance(value, dict):
        for item in value.values():
            result.update(protected_paths(item))
    elif isinstance(value, list):
        for item in value:
            result.update(protected_paths(item))
    elif isinstance(value, str) and len(value) < 4096:
        try:
            path = Path(value)
            if path.is_file():
                result.add(path.resolve())
        except (OSError, ValueError):
            pass
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest")
    parser.add_argument("--previous-review", help="Compare the preserved prior review context; does not authorize semantic changes")
    parser.add_argument("--output", help="New JSON report; refuses overwrite")
    parser.add_argument("--strict", action="store_true", help="Exit 1 unless all evidence layers are complete")
    args = parser.parse_args(argv)
    try:
        document = load_json(args.manifest)
        report = delivery_report(document)
        report["manifest"] = {"path": str(Path(args.manifest).resolve()), "sha256": sha256_file(args.manifest)}
        protected = protected_paths(document) | {Path(args.manifest).resolve()}
        if args.previous_review:
            previous = load_json(args.previous_review)
            report["revision"] = revision_impact(previous, document)
            report["previous_review"] = {"path": str(Path(args.previous_review).resolve()), "sha256": sha256_file(args.previous_review)}
            protected |= protected_paths(previous) | {Path(args.previous_review).resolve()}
        if args.output:
            if Path(args.output).resolve() in protected:
                raise CliError("delivery output aliases an input")
            atomic_write_json(args.output, report)
        emit_json(report)
        return 1 if args.strict and report["status"] != "evidence_complete" else 0
    except (CliError, OSError, KeyError, TypeError, ValueError) as exc:
        parser.exit(2, f"error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
