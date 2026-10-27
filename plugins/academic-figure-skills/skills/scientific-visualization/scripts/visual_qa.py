#!/usr/bin/env python3
"""Deterministic in-process layout checks plus a safe final-size preview."""

from __future__ import annotations

import argparse
import io
import logging
import os
import sys
import tempfile
import warnings
from pathlib import Path
from typing import Any

from _common import CliError, checked_output_file, emit_json, positive_float

SCHEMA_VERSION = "1.0"
GLYPH_MARKERS = ("missing from font", "Glyph", "findfont")


class _GlyphHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.messages: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        message = record.getMessage()
        if any(marker in message for marker in GLYPH_MARKERS):
            self.messages.append(message)


def _draw_and_collect(fig: Any) -> list[str]:
    handler = _GlyphHandler()
    logger = logging.getLogger("matplotlib")
    previous_level = logger.level
    logger.setLevel(logging.WARNING)
    logger.addHandler(handler)
    collected: list[str] = []
    try:
        with warnings.catch_warnings(record=True) as warning_records:
            warnings.simplefilter("always")
            buffer = io.BytesIO()
            fig.savefig(buffer, format="png", dpi=100)
            buffer.close()
        collected.extend(
            str(item.message)
            for item in warning_records
            if any(marker in str(item.message) for marker in GLYPH_MARKERS)
        )
    finally:
        logger.removeHandler(handler)
        logger.setLevel(previous_level)
    collected.extend(handler.messages)
    return list(dict.fromkeys(collected))


def _overlap(labels: list[Any], renderer: Any, *, axis: str, tolerance: float) -> bool:
    boxes = []
    for label in labels:
        try:
            if label.get_visible() and label.get_text().strip():
                boxes.append(label.get_window_extent(renderer))
        except Exception:
            continue
    if len(boxes) < 2:
        return False
    if axis == "x":
        boxes.sort(key=lambda box: box.x0)
        return any(first.x1 - second.x0 > tolerance for first, second in zip(boxes, boxes[1:]))
    boxes.sort(key=lambda box: box.y0)
    return any(first.y1 - second.y0 > tolerance for first, second in zip(boxes, boxes[1:]))


def audit_figure(
    fig: Any,
    *,
    clip_tolerance_px: float = 2.0,
    overlap_tolerance_px: float = 1.0,
) -> dict[str, Any]:
    """Measure glyph warnings, non-tick text clipping, and tick overlap."""
    try:
        import matplotlib.text as matplotlib_text
    except ImportError as exc:
        raise CliError(
            "Matplotlib is required for visual QA; run with --with 'matplotlib==3.11.1'"
        ) from exc

    findings: list[dict[str, Any]] = []
    glyph_messages = _draw_and_collect(fig)
    if glyph_messages:
        findings.append(
            {
                "check_id": "text.missing_glyph",
                "layer": "textual",
                "status": "blocked",
                "message": "Matplotlib reported missing glyphs or unresolved fonts.",
                "evidence": glyph_messages[:10],
            }
        )

    try:
        renderer = fig.canvas.get_renderer()
    except Exception:
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
    width = float(fig.bbox.width)
    height = float(fig.bbox.height)

    tick_ids: set[int] = set()
    for axis in fig.axes:
        tick_ids.update(
            id(label)
            for label in (
                *axis.get_xticklabels(),
                *axis.get_xticklabels(minor=True),
                *axis.get_yticklabels(),
                *axis.get_yticklabels(minor=True),
            )
        )

    clipped = []
    for text in fig.findobj(matplotlib_text.Text):
        try:
            if id(text) in tick_ids or not text.get_visible() or not text.get_text().strip():
                continue
            box = text.get_window_extent(renderer)
        except Exception:
            continue
        if (
            box.x0 < -clip_tolerance_px
            or box.y0 < -clip_tolerance_px
            or box.x1 > width + clip_tolerance_px
            or box.y1 > height + clip_tolerance_px
        ):
            clipped.append(text.get_text().strip().replace("\n", " ")[:80])
    if clipped:
        findings.append(
            {
                "check_id": "visual.text_outside_canvas",
                "layer": "visual",
                "status": "review",
                "message": "Non-tick text extends outside the figure canvas.",
                "evidence": list(dict.fromkeys(clipped))[:20],
            }
        )

    overlaps = []
    for index, axis in enumerate(fig.axes):
        for direction, labels in (
            ("x", axis.get_xticklabels()),
            ("y", axis.get_yticklabels()),
        ):
            if _overlap(labels, renderer, axis=direction, tolerance=overlap_tolerance_px):
                overlaps.append({"axes_index": index, "axis": direction})
    if overlaps:
        findings.append(
            {
                "check_id": "visual.tick_overlap",
                "layer": "visual",
                "status": "review",
                "message": "Adjacent tick-label bounding boxes overlap.",
                "evidence": overlaps,
            }
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "checks": {
            "numeric": {
                "status": "not_checked",
                "notice": "Numeric mapping requires comparison with source data and transformations.",
            },
            "textual": {
                "status": "blocked" if glyph_messages else "pass",
                "automated_scope": ["Matplotlib missing-glyph and font-resolution warnings"],
            },
            "visual": {
                "status": "review" if clipped or overlaps else "pass",
                "automated_scope": ["canvas bounds for non-tick text", "adjacent tick-label overlap"],
            },
        },
        "findings": findings,
        "manual_review_required": [
            "numeric mapping against source data",
            "units, caption, legend, and uncertainty semantics",
            "legend/data occlusion and annotation collisions",
            "panel alignment and cross-panel mapping consistency",
            "legibility, contrast, and redundant encoding at final size",
        ],
        "notice": (
            "Automated PASS covers only the listed deterministic checks and is "
            "not a scientific or visual-quality certificate."
        ),
    }


def render_preview(
    fig: Any,
    output: str | Path,
    *,
    dpi: float = 150.0,
    overwrite: bool = False,
) -> Path:
    """Write a preview atomically without changing the figure page dimensions."""
    destination = checked_output_file(output, force=overwrite)
    if destination.suffix.lower() != ".png":
        raise CliError("preview output must use a .png suffix")
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.stem}.", suffix=".png", dir=destination.parent
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        temporary.unlink()
        import matplotlib as mpl

        with mpl.rc_context({"savefig.bbox": None}):
            fig.savefig(temporary, format="png", dpi=float(dpi), bbox_inches=None)
        if not temporary.exists() or temporary.stat().st_size == 0:
            raise CliError("Matplotlib produced no preview data")
        if destination.exists() and not overwrite:
            raise CliError(f"refusing to overwrite existing output: {destination}")
        os.replace(temporary, destination)
    except CliError:
        raise
    except Exception as exc:
        raise CliError(f"failed to render preview: {exc}") from exc
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass
    return destination


def _demo(output: str, *, dpi: float, overwrite: bool) -> dict[str, Any]:
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise CliError(
            "Matplotlib is required for visual QA; run with --with 'matplotlib==3.11.1'"
        ) from exc
    fig, axis = plt.subplots(figsize=(3.0, 2.0))
    labels = [f"long_condition_{index}" for index in range(10)]
    axis.bar(range(len(labels)), [index + 1 for index in range(len(labels))])
    axis.set_xticks(range(len(labels)), labels)
    axis.set_title("Deliberately long title extending beyond a narrow demo canvas")
    try:
        report = audit_figure(fig)
        preview = render_preview(fig, output, dpi=dpi, overwrite=overwrite)
    finally:
        plt.close(fig)
    report["preview"] = str(preview.resolve())
    report["demo"] = "known-bad tick overlap and possible title clipping"
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run deterministic in-process Matplotlib figure checks and render a preview."
    )
    parser.add_argument("--demo", metavar="OUTPUT.png", help="generate and audit a known-bad demo")
    parser.add_argument("--dpi", type=positive_float, default=150.0)
    parser.add_argument("--force", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
        if not args.demo:
            raise CliError(
                "CLI mode requires --demo; real figures should call audit_figure(fig) before export"
            )
        emit_json(_demo(args.demo, dpi=args.dpi, overwrite=args.force))
        return 0
    except CliError as exc:
        parser.exit(2, f"error: {exc}\n")


if __name__ == "__main__":
    sys.exit(main())
