#!/usr/bin/env python3
"""Read-only poster scale audit and optional measured text wrapping."""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path


def positive(value: str) -> float:
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("value must be finite and positive")
    return number


def visible_text(value: str) -> str:
    return html.unescape(re.sub(r"<[^>]*>", "", value)).strip()


def audit(xml: str, source_width: float, display_width: float,
          primary: set[str], secondary: set[str], primary_min: float = 14,
          secondary_min: float = 10) -> dict:
    if any(not math.isfinite(x) or x <= 0 for x in
           (source_width, display_width, primary_min, secondary_min)):
        raise ValueError("widths and review thresholds must be finite and positive")
    if primary & secondary:
        raise ValueError("an ID cannot have both roles")
    if "<!DOCTYPE" in xml.upper() or "<!ENTITY" in xml.upper():
        raise ValueError("DTD/entity declarations are not supported")
    root = ET.fromstring(xml)
    models = list(root.iter("mxGraphModel"))
    if len(models) != 1 or len(list(root.iter("diagram"))) > 1:
        raise ValueError("provide exactly one uncompressed Draw.io page")
    cells = list(models[0].iter("mxCell"))
    ids = [c.get("id") for c in cells]
    if None in ids or len(set(ids)) != len(ids):
        raise ValueError("missing or duplicate cell IDs")
    labels = {c.get("id"): c for c in cells if visible_text(c.get("value", ""))}
    unknown = (primary | secondary) - labels.keys()
    if unknown:
        raise ValueError(f"role IDs have no visible label: {sorted(unknown)}")
    scale = display_width / source_width
    records = []
    for cell_id, cell in labels.items():
        style = dict(part.split("=", 1) for part in cell.get("style", "").split(";") if "=" in part)
        role = "primary" if cell_id in primary else "secondary" if cell_id in secondary else "unclassified"
        issues = [] if role != "unclassified" else ["role_not_classified"]
        nominal = None
        try:
            size = float(style.get("fontSize", "nan"))
            if not math.isfinite(size) or size <= 0:
                raise ValueError
            nominal = size * scale
            threshold = primary_min if role == "primary" else secondary_min
            if nominal < threshold:
                issues.append("below_review_threshold")
        except ValueError:
            issues.append("font_size_unknown")
        records.append({"id": cell_id, "text": visible_text(cell.get("value", "")),
                        "role": role, "display_font_px": None if nominal is None else round(nominal, 3),
                        "issues": issues})
    issues_found = not records or any(r["issues"] for r in records)
    return {"status": "review" if issues_found else "clear", "source_width": source_width,
            "display_width": display_width, "scale": scale,
            "scope": "Nominal text scale only; no visual, semantic or usability certification.",
            "issues": ["no_visible_labels"] if not records else [], "labels": records}


def tokens(text: str, keep: list[str]) -> list[str]:
    protected = "|".join(re.escape(x) for x in sorted(set(keep), key=len, reverse=True) if x)
    pattern = (protected + "|" if protected else "") + r"[A-Za-z0-9]+(?:[._/+:-][A-Za-z0-9]+)*|[ \t]+|."
    result: list[str] = []
    for token in re.findall(pattern, text):
        if result and unicodedata.combining(token[0]):
            result[-1] += token
        else:
            result.append(token)
    return result


def wrap_text(text: str, measure, width: float, keep: list[str] | None = None) -> list[str]:
    if not math.isfinite(width) or width <= 0:
        raise ValueError("width must be finite and positive")
    closing = set("，。！？；：、）】》」』,.;:!?)]}")
    opening = set("（【《「『([{")
    lines: list[str] = []
    for paragraph in text.split("\n"):
        current: list[str] = []
        for token in tokens(paragraph, keep or []):
            if measure(token) > width:
                raise ValueError(f"unbreakable token exceeds width: {token!r}")
            if current and measure("".join(current) + token) > width:
                carry: list[str] = []
                # Keep closing punctuation with its preceding token and opening
                # punctuation with its following token; never invent a blank line.
                if token[0] in closing or current[-1][-1] in opening:
                    carry.insert(0, current.pop())
                if not current and carry:
                    raise ValueError("box is too narrow for punctuation and its adjacent token")
                lines.append("".join(current).rstrip())
                current = carry
                if not current and token.isspace():
                    continue
                if measure("".join(current) + token) > width:
                    raise ValueError("punctuation group exceeds width")
            current.append(token)
        lines.append("".join(current).rstrip())
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    a = commands.add_parser("audit", help="Audit nominal font sizes at a declared viewing width")
    a.add_argument("drawio", type=Path)
    a.add_argument("--source-width", type=positive, required=True)
    a.add_argument("--display-width", type=positive, required=True)
    a.add_argument("--primary-ids", default="")
    a.add_argument("--secondary-ids", default="")
    a.add_argument("--primary-min", type=positive, default=14)
    a.add_argument("--secondary-min", type=positive, default=10)
    w = commands.add_parser("wrap", help="Measure a supplied font and suggest display line breaks")
    w.add_argument("text_file", type=Path)
    w.add_argument("--font", type=Path, required=True)
    w.add_argument("--font-size", type=int, required=True)
    w.add_argument("--width", type=positive, required=True)
    w.add_argument("--keep", action="append", default=[])
    w.add_argument("--collapse-newlines", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "audit":
            split = lambda value: {x.strip() for x in value.split(",") if x.strip()}
            result = audit(args.drawio.read_text(encoding="utf-8"), args.source_width,
                           args.display_width, split(args.primary_ids), split(args.secondary_ids),
                           args.primary_min, args.secondary_min)
            code = 0 if result["status"] == "clear" else 1
        else:
            if args.font_size <= 0:
                raise ValueError("font size must be positive")
            try:
                from PIL import ImageFont
            except ImportError as exc:
                raise ValueError("wrap needs local Pillow; audit does not. No dependency was installed.") from exc
            original = args.text_file.read_text(encoding="utf-8")
            text = original.replace("\r\n", "\n").rstrip("\n")
            if args.collapse_newlines:
                text = re.sub(r"\s*\n\s*", " ", text)
            font = ImageFont.truetype(str(args.font), args.font_size)
            lines = wrap_text(text, font.getlength, args.width, args.keep)
            result = {"status": "measured", "original": original, "lines": lines,
                      "widths": [round(font.getlength(x), 3) for x in lines],
                      "font": str(args.font), "font_sha256": hashlib.sha256(args.font.read_bytes()).hexdigest(),
                      "font_size": args.font_size, "available_width": args.width,
                      "scope": "Suggested breaks in the supplied font; inspect the actual rendered export."}
            code = 0
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return code
    except (OSError, ValueError, ET.ParseError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    sys.exit(main())
