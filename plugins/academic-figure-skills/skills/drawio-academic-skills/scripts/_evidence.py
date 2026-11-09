"""Replay independent evidence checks without gating one layer on another's PASS."""
from pathlib import Path

from _common import load_json, sha256_file
from _validation import CheckExecution
from audit_figure_geometry import verify_evidence


def _problem(findings, code, path, message, severity='error'):
    findings.append(dict(code=code, path=path, message=message, severity=severity))


def _run(execution, name, findings, path, check, severity='error'):
    try:
        check()
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        execution.blocked.append(f'{name}: {exc}')
        _problem(findings, 'review_evidence_unavailable', path, str(exc), severity)
    else:
        execution.executed.append(name)


def check_geometry(geometry, artifacts, inventory, findings, *, finalizing):
    execution = CheckExecution()
    severity = 'error' if finalizing else 'warning'
    if not isinstance(geometry, dict) or not geometry:
        execution.blocked.append('geometry evidence missing')
        if finalizing:
            _problem(findings, 'geometry_evidence_missing', 'qa.geometry',
                     'accepted/strict delivery requires a current replayable geometry audit')
        return execution
    declared_svg = next((x.get('path') for x in artifacts if x.get('role') == 'svg'), None)
    svg = geometry.get('svg') or declared_svg

    def replay():
        messages = []
        if not svg:
            messages.append('geometry SVG input is missing')
            execution.blocked.append('geometry SVG input missing')
        else:
            if declared_svg and Path(svg).resolve() != Path(declared_svg).resolve():
                messages.append('geometry input differs from the delivered SVG')
            messages.extend(verify_evidence(svg, geometry))
        for message in messages:
            _problem(findings, 'geometry_evidence_invalid', 'qa.geometry', message, severity)

    _run(execution, 'geometry replay', findings, 'qa.geometry', replay, severity)
    if finalizing:
        def coverage():
            scene = load_json(geometry['scene'])
            if any({x['id'] for x in scene[kind]} != {x['id'] for x in inventory[kind]}
                   for kind in ('nodes', 'edges')):
                _problem(findings, 'geometry_inventory_mismatch', 'qa.geometry',
                         'scene IDs must cover the declared inventory exactly')
        _run(execution, 'inventory coverage', findings, 'qa.geometry', coverage)
    return execution


def check_visual(visual, findings, *, finalizing):
    execution = CheckExecution()
    if not finalizing:
        execution.blocked.append('visual replay requires strict/accepted validation')
        return execution
    visual = visual if isinstance(visual, dict) else {}
    if visual.get('status') != 'pass' or visual.get('issues'):
        _problem(findings, 'visual_review_incomplete', 'qa.visual',
                 'accepted/strict delivery requires closed visual findings and pass status')

    def artifact():
        if not visual.get('artifact') or visual.get('sha256') != sha256_file(visual['artifact']):
            _problem(findings, 'visual_review_stale', 'qa.visual',
                     'visual review must hash the actual inspected current artifact')
    _run(execution, 'visual artifact binding', findings, 'qa.visual', artifact)
    return execution


def check_scientific(scientific, artifacts, findings, *, finalizing, geometry_svg=None):
    execution = CheckExecution()
    if not finalizing:
        execution.blocked.append('scientific replay requires strict/accepted validation')
        return execution
    scientific = scientific if isinstance(scientific, dict) else {}
    # PDF/PNG delivery may keep the geometry SVG as diagnostic evidence only.
    # Prefer the delivered SVG when present; no geometry PASS is required here.
    svg = next((x.get('path') for x in artifacts if x.get('role') == 'svg'), None) or geometry_svg

    def binding():
        if (scientific.get('status') != 'pass' or not scientific.get('basis') or not svg
                or scientific.get('svg_sha256') != sha256_file(svg)):
            _problem(findings, 'scientific_review_incomplete', 'qa.scientific',
                     'record the current scientific/semantic review basis separately from geometry')
    _run(execution, 'scientific SVG binding', findings, 'qa.scientific', binding)
    sources = scientific.get('sources')
    if not isinstance(sources, list) or not sources:
        execution.blocked.append('scientific sources missing')
        _problem(findings, 'scientific_sources_missing', 'qa.scientific.sources',
                 'record source evidence, or an explicit non-empirical contract file')
    else:
        for index, source in enumerate(sources):
            def source_binding():
                if source.get('sha256') != sha256_file(source['path']):
                    _problem(findings, 'scientific_source_stale', 'qa.scientific.sources',
                             'a reviewed source changed')
            _run(execution, f'scientific source {index}', findings,
                 'qa.scientific.sources', source_binding)
    return execution
