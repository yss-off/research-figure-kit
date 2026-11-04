#!/usr/bin/env python3
"""Audit arrow landing space in exported SVG polylines without changing artwork.

This is a geometry preflight, not a renderer, general SVG implementation, or
publication/readability approval. Curves/transformed edges require visual review.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from _common import CliError, atomic_write_json, checked_input_file

TOKEN = re.compile(r"[A-Za-z]|[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?")


def polyline(element: ET.Element) -> list[tuple[float, float]]:
    kind = element.tag.rsplit('}', 1)[-1]
    if kind == 'line':
        return [(float(element.get('x1', '0')), float(element.get('y1', '0'))),
                (float(element.get('x2', '0')), float(element.get('y2', '0')))]
    if kind == 'polyline':
        values = [float(v) for v in re.split(r'[\s,]+', element.get('points', '').strip()) if v]
        if len(values) % 2:
            raise ValueError('odd polyline coordinate count')
        return list(zip(values[::2], values[1::2]))
    if kind != 'path':
        raise ValueError(f'unsupported marked geometry: {kind}')
    raw = element.get('d', '')
    if re.sub(r'[\s,]', '', TOKEN.sub('', raw)):
        raise ValueError('unsupported path syntax')
    tokens = TOKEN.findall(raw)
    points: list[tuple[float, float]] = []
    position = (0.0, 0.0)
    index = 0
    command = ''
    while index < len(tokens):
        if tokens[index].isalpha():
            command = tokens[index]
            index += 1
        if command not in {'M', 'm', 'L', 'l', 'H', 'h', 'V', 'v'}:
            raise ValueError('only single-subpath M/L/H/V polylines are audited')
        count = 1 if command.upper() in {'H', 'V'} else 2
        values = tokens[index:index + count]
        if len(values) != count or any(v.isalpha() for v in values):
            raise ValueError('incomplete path coordinate')
        numbers = list(map(float, values))
        if command.upper() == 'M' and points:
            raise ValueError('multiple subpaths are not audited')
        if command.upper() == 'H':
            point = (numbers[0] + (position[0] if command.islower() else 0), position[1])
        elif command.upper() == 'V':
            point = (position[0], numbers[0] + (position[1] if command.islower() else 0))
        else:
            point = (numbers[0] + (position[0] if command.islower() else 0),
                     numbers[1] + (position[1] if command.islower() else 0))
        points.append(point)
        position = point
        if command in {'M', 'm'}:
            command = 'l' if command == 'm' else 'L'
        index += count
    if len(points) < 2 or not all(math.isfinite(v) for p in points for v in p):
        raise ValueError('polyline needs at least two finite points')
    return points


def landing_run(points: list[tuple[float, float]], tolerance: float) -> float:
    """Length of the final straight run, ignoring duplicate/subpixel jitter."""
    end = points[-1]
    previous = next((p for p in reversed(points[:-1]) if math.dist(p, end) > tolerance), None)
    if previous is None:
        return 0.0
    dx, dy = end[0] - previous[0], end[1] - previous[1]
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length
    run = 0.0
    for point in reversed(points[:-1]):
        px, py = end[0] - point[0], end[1] - point[1]
        projection = px * ux + py * uy
        if abs(px * uy - py * ux) > tolerance or projection < run - tolerance:
            break
        run = max(run, projection)
    return run


def marker_extent(marker: ET.Element, stroke_width: float) -> float:
    """Conservative backward extent of the marker viewport in SVG user units."""
    viewbox = [float(v) for v in re.split(r'[\s,]+', marker.get('viewBox', '').strip()) if v]
    if len(viewbox) != 4 or viewbox[2] <= 0 or viewbox[3] <= 0:
        raise ValueError('marker needs a positive viewBox')
    if marker.get('orient', '') not in {'auto', 'auto-start-reverse'}:
        raise ValueError('fixed marker orientation requires manual review')
    width = float(marker.get('markerWidth', '3'))
    height = float(marker.get('markerHeight', '3'))
    ref_x = float(marker.get('refX', '0'))
    units = marker.get('markerUnits', 'strokeWidth')
    if units not in {'strokeWidth', 'userSpaceOnUse'}:
        raise ValueError('unsupported markerUnits')
    if marker.get('preserveAspectRatio', 'xMidYMid meet') != 'xMidYMid meet':
        raise ValueError('non-default marker aspect ratio requires manual review')
    values = [width, height, ref_x, stroke_width, *viewbox]
    if not all(math.isfinite(v) for v in values) or min(width, height, stroke_width) <= 0:
        raise ValueError('invalid marker geometry')
    if not viewbox[0] <= ref_x <= viewbox[0] + viewbox[2]:
        raise ValueError('marker reference outside viewBox requires manual review')
    scale = min(width / viewbox[2], height / viewbox[3])
    return (ref_x - viewbox[0]) * scale * (stroke_width if units == 'strokeWidth' else 1)


def audit_svg(svg: str, *, tolerance: float = 0.1, orthogonal: bool = False) -> dict:
    root = ET.fromstring(svg)
    markers = {e.get('id'): e for e in root.iter() if e.tag.rsplit('}', 1)[-1] == 'marker'}
    findings = []
    measurements = []
    edge_index = 0
    parents = {child: parent for parent in root.iter() for child in parent}
    for element in root.iter():
        # Inline CSS can introduce markers without presentation attributes.
        # We do not implement a CSS cascade: report it instead of skipping it.
        # Comments can occur before a declaration or between its name and colon.
        # Fail closed on comment-bearing styles instead of pretending to parse CSS.
        style = element.get('style', '')
        if '/*' in style or re.search(
                r'(?:^|;)\s*(?:marker(?:-start|-mid|-end)?|stroke-width|transform)\s*:',
                style, re.IGNORECASE):
            findings.append(dict(code='not_audited', severity='review',
                                 reason='SVG inline connector style or CSS comments require manual review'))
        ends = [(side, element.get(f'marker-{side}')) for side in ('start', 'end')
                if element.get(f'marker-{side}') and element.get(f'marker-{side}') != 'none']
        if not ends:
            continue
        edge_index += 1
        try:
            ancestor = element
            stroke_width = None
            while ancestor is not None:
                if stroke_width is None and ancestor.get('stroke-width') is not None:
                    value = ancestor.get('stroke-width').strip()
                    if value != 'inherit':
                        stroke_width = float(value)
                if ancestor.get('transform') or ancestor.get('style') and re.search(
                        r'(?:^|;)\s*(?:stroke-width|marker-start|marker-end|transform)\s*:', ancestor.get('style', '')):
                    raise ValueError('transformed or CSS-sized markers require manual review')
                ancestor = parents.get(ancestor)
            points = polyline(element)
            if len(points) < 2 or not all(math.isfinite(v) for p in points for v in p):
                raise ValueError("polyline needs at least two finite points")
            if orthogonal:
                for a, b in zip(points, points[1:]):
                    if abs(a[0] - b[0]) > tolerance and abs(a[1] - b[1]) > tolerance:
                        findings.append(dict(code='non_orthogonal_segment', edge_index=edge_index,
                                             severity='warning', segment=[a, b]))
            for side, reference in ends:
                match = re.fullmatch(r'url\(#([^\s)]+)\)', reference)
                if not match or match[1] not in markers:
                    raise ValueError('unresolved or external marker')
                sequence = list(reversed(points)) if side == 'start' else points
                run = landing_run(sequence, tolerance)
                extent = marker_extent(markers[match[1]], 1.0 if stroke_width is None else stroke_width)
                record = dict(edge_index=edge_index, side=side, endpoint=sequence[-1],
                              straight_run=round(run, 4), marker_extent=round(extent, 4))
                measurements.append(record)
                if run + tolerance < extent:
                    findings.append(dict(code='arrowhead_over_bend', severity='warning', **record))
        except (ValueError, TypeError, OverflowError) as error:
            findings.append(dict(code='not_audited', edge_index=edge_index, severity='review', reason=str(error)))
    # CSS can put markers on unmarked paths, so a numeric PASS would be misleading.
    if any(e.tag.rsplit('}', 1)[-1] == 'style' for e in root.iter()):
        findings.append(dict(code='not_audited', severity='review', reason='SVG stylesheet requires manual review'))
    status = 'review' if any(f['severity'] == 'review' for f in findings) else 'warning' if findings else 'pass'
    return dict(status=status, audited_marked_edges=edge_index, measurements=measurements, findings=findings,
                scope='SVG marker landing space only; viewBox estimate excludes stroke caps/filter effects; '
                      'does not certify attachment, semantic relations, label clearance, or readability')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('svg', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--force', action='store_true', help='Overwrite an existing report, never the input SVG')
    parser.add_argument('--orthogonal', action='store_true', help='Also flag diagonal polyline segments')
    parser.add_argument('--strict', action='store_true', help='Return nonzero for warnings as well as unaudited geometry')
    args = parser.parse_args()
    try:
        source = checked_input_file(args.svg)
        if args.output and (args.output.resolve() == source or
                            args.output.exists() and args.output.samefile(source)):
            raise CliError('output must not refer to the input SVG')
        result = audit_svg(source.read_text(encoding='utf-8'), orthogonal=args.orthogonal)
        if args.output:
            atomic_write_json(args.output, result, force=args.force)
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
    except (OSError, UnicodeError, CliError, ET.ParseError) as error:
        parser.exit(2, f'{error}\n')
    return 2 if result['status'] == 'review' else 1 if args.strict and result['status'] == 'warning' else 0


if __name__ == '__main__':
    raise SystemExit(main())
