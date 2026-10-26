#!/usr/bin/env python3
"""Focused P0 regression tests using only temporary artifacts."""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

EVAL_ROOT = Path(__file__).resolve().parent
SKILL_ROOT = EVAL_ROOT.parent
SCRIPT_ROOT = SKILL_ROOT / "scripts"
sys.path.insert(0, str(SCRIPT_ROOT))

from _common import CliError  # noqa: E402
from profile_data import profile_sources, render_markdown  # noqa: E402


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class EvalInventoryTests(unittest.TestCase):
    def test_case_inventory_and_schema(self) -> None:
        acceptance = json.loads((EVAL_ROOT / "acceptance.json").read_text(encoding="utf-8"))
        mapping = {
            "trigger_cases": "trigger_cases.json",
            "chart_choice_cases": "chart_choice_cases.json",
            "known_bad_cases": "known_bad_cases.json",
        }
        for key, filename in mapping.items():
            cases = json.loads((EVAL_ROOT / filename).read_text(encoding="utf-8"))
            self.assertGreaterEqual(len(cases), acceptance["minimum_case_counts"][key])
            self.assertEqual(len({case["id"] for case in cases}), len(cases))


class ProfilerTests(unittest.TestCase):
    def test_read_only_deterministic_profile_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "observations.csv"
            source.write_text(
                "subject,treatment,response,note\n"
                "s1,control,1.0,ok\n"
                "s2,control,,missing response\n"
                "s3,drug,100.0,ok\n"
                "s3,drug,100.0,ok\n",
                encoding="utf-8",
            )
            before = _hash(source)
            first = profile_sources([source], group_columns=["treatment"])
            second = profile_sources([source], group_columns=["treatment"])
            after = _hash(source)

            self.assertEqual(before, after)
            self.assertEqual(first, second)
            self.assertEqual(first["schema_version"], "1.0")
            self.assertEqual(first["profiles"][0]["table"]["duplicate_rows"]["count"], 1)
            self.assertIn("heuristics", first["settings"])
            markdown = render_markdown(first)
            self.assertIn("# Data profile", markdown)
            self.assertIn("missing_values_present", markdown)

    def test_multiple_files_are_not_joined(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "a.csv"
            second = Path(directory) / "b.tsv"
            first.write_text("x\n1\n", encoding="utf-8")
            second.write_text("y\n2\n", encoding="utf-8")
            report = profile_sources(
                [first, second], missing_values=(value for value in ["", "NA"])
            )
            self.assertEqual(len(report["profiles"]), 2)
            self.assertTrue(report["settings"]["files_profiled_separately"])
            self.assertEqual(report["settings"]["missing_values"], ["", "NA"])


class MatplotlibTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        try:
            import matplotlib  # noqa: F401
        except ImportError as exc:
            raise unittest.SkipTest("Matplotlib is not installed") from exc

    def test_visual_qa_detects_overlap_and_preview_refuses_overwrite(self) -> None:
        import matplotlib.pyplot as plt

        from visual_qa import audit_figure, render_preview

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "preview.png"
            fig, axis = plt.subplots(figsize=(2.6, 1.8))
            labels = [f"long_condition_{index}" for index in range(10)]
            axis.bar(range(10), range(10))
            axis.set_xticks(range(10), labels)
            try:
                report = audit_figure(fig)
                render_preview(fig, output)
                self.assertTrue(any(item["check_id"] == "visual.tick_overlap" for item in report["findings"]))
                with self.assertRaises(CliError):
                    render_preview(fig, output)
            finally:
                plt.close(fig)

    def test_font_preflight_has_concrete_paths(self) -> None:
        from font_preflight import preflight_fonts

        report = preflight_fonts("ASCII − 中文")
        self.assertIn(report["status"], {"pass", "review"})
        self.assertTrue(report["font_stack"])
        self.assertTrue(all(Path(item["path"]).is_file() for item in report["font_stack"]))

    def test_preview_preserves_dimensions_under_global_tight_bbox(self) -> None:
        import struct
        import matplotlib as mpl
        import matplotlib.pyplot as plt
        from visual_qa import render_preview

        fig, axis = plt.subplots(figsize=(4, 3))
        axis.plot([0, 1], [0, 1])
        try:
            with tempfile.TemporaryDirectory() as directory, mpl.rc_context({"savefig.bbox": "tight"}):
                for dpi in (100, 150):
                    output = render_preview(fig, Path(directory) / f"preview-{dpi}.png", dpi=dpi)
                    # PNG IHDR records the actual exported width and height.
                    width, height = struct.unpack(">II", output.read_bytes()[16:24])
                    self.assertEqual((4 * dpi, 3 * dpi), (width, height))
                    self.assertEqual("tight", mpl.rcParams["savefig.bbox"])
                self.assertEqual([4, 3], list(fig.get_size_inches()))
        finally:
            plt.close(fig)

    def test_export_workflow_extension_and_no_overwrite(self) -> None:
        import matplotlib.pyplot as plt

        from figure_export import export_figure

        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory) / "figure"
            fig, axis = plt.subplots()
            axis.plot([0, 1], [0, 1])
            try:
                report = export_figure(
                    fig,
                    base,
                    formats=["png"],
                    provenance={"raw_data": "synthetic"},
                    workflow={
                        "figure_contract": {"scientific_question": "smoke test"},
                        "chart_selection": {"recommended_chart": "line"},
                        "qa": {"numeric": {"status": "not_checked"}},
                    },
                    write_manifest=True,
                )
                self.assertEqual(report["workflow"]["schema_version"], "1.0")
                self.assertTrue((Path(directory) / "figure.export.json").is_file())
                with self.assertRaises(CliError):
                    export_figure(fig, base, formats=["png"])
            finally:
                plt.close(fig)


if __name__ == "__main__":
    unittest.main(verbosity=2)
