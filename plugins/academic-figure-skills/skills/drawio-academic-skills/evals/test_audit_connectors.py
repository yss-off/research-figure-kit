"""Regressions derived from exported arrows, without client figure content."""
import sys
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from audit_connectors import audit_svg


def drawing(path='M 0 0 L 40 0 L 40 8', width='2.25', units='', marker_attr='', tag=None):
    edge = tag or f'<path d="{path}" stroke-width="{width}" marker-end="url(#a)"/>'
    return f'''<svg xmlns="http://www.w3.org/2000/svg"><defs>
    <marker id="a" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="8" markerHeight="8"
      orient="auto-start-reverse" {units} {marker_attr}><path d="M 0 0 L 10 5 L 0 10"/></marker>
    </defs>{edge}</svg>'''


class ConnectorAuditTests(unittest.TestCase):
    def test_inherited_stroke_width_matches_explicit_width(self):
        edge = '<path d="M 0 0 L 40 0 L 40 20" marker-end="url(#a)"/>'
        for inherited in ('4', 'inherit'):
            tag = f'<g stroke-width="4"><g stroke-width="{inherited}">{edge}</g></g>'
            report = audit_svg(drawing(tag=tag))
            self.assertEqual('warning', report['status'])
            self.assertEqual(32, report['measurements'][0]['marker_extent'])
        # A child's presentation attribute overrides its parent's value.
        tag = '<g stroke-width="4">' + edge.replace('<path ', '<path stroke-width="1" ') + '</g>'
        self.assertEqual('pass', audit_svg(drawing(tag=tag))['status'])

    def test_inline_markers_without_presentation_attributes_require_review(self):
        for style in ('marker-end:url(#a);stroke-width:4', 'marker:url(#a)',
                      'MARKER-END: url(#a) !important'):
            tag = f'<path d="M 0 0 L 40 0 L 40 8" style="{style}"/>'
            self.assertEqual('review', audit_svg(drawing(tag=tag))['status'])

    def test_commented_inline_styles_fail_closed(self):
        for style in ('/* arrow */ marker-end:url(#a)',
                      'fill:none; /* arrow */ marker-end:url(#a)',
                      'marker-end/**/:url(#a)',
                      '/* first\nsecond */ marker-start:url(#a)',
                      '/* unterminated', 'fill:red /* decoration */'):
            with self.subTest(style=style):
                tag = f'<path d="M 0 0 L 40 0 L 40 8" stroke-width="4" style="{style}"/>'
                report = audit_svg(drawing(tag=tag))
                self.assertEqual('review', report['status'])
                self.assertTrue(any(f['code'] == 'not_audited' for f in report['findings']))
        tag = '<path d="M 0 0 L 40 0 L 40 32" style="fill:none" marker-end="url(#a)"/>'
        self.assertEqual('pass', audit_svg(drawing(tag=tag))['status'])

    def test_commented_inline_marker_cli_requires_review(self):
        script = Path(__file__).resolve().parents[1] / 'scripts' / 'audit_connectors.py'
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'commented.svg'
            original = drawing(tag='<path d="M 0 0 L 40 0 L 40 8" '
                                   'stroke-width="4" style="/* arrow */ marker-end:url(#a)"/>')
            source.write_text(original, encoding='utf-8')
            for flags in ([], ['--strict']):
                result = subprocess.run([sys.executable, str(script), str(source), *flags],
                                        capture_output=True, text=True)
                self.assertEqual(2, result.returncode)
                self.assertEqual('review', json.loads(result.stdout)['status'])
                self.assertEqual(original, source.read_text(encoding='utf-8'))

    def test_cli_protects_input_and_existing_reports(self):
        script = Path(__file__).resolve().parents[1] / 'scripts' / 'audit_connectors.py'
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'source.svg'
            original = drawing('M 0 0 L 40 0 L 40 32')
            source.write_text(original, encoding='utf-8')

            def run(output, *flags):
                return subprocess.run([sys.executable, str(script), str(source),
                                       '--output', str(output), *flags], capture_output=True)

            alias = Path(directory) / 'alias.svg'
            os.link(source, alias)
            symlink = Path(directory) / 'linked.svg'
            symlink.symlink_to(source)
            for output in (source, alias, symlink):
                for flags in ((), ('--force',)):
                    self.assertEqual(2, run(output, *flags).returncode)
                    self.assertEqual(original, source.read_text(encoding='utf-8'))
            report = Path(directory) / 'report.json'
            report.write_text('existing report', encoding='utf-8')
            self.assertEqual(2, run(report).returncode)
            self.assertEqual('existing report', report.read_text(encoding='utf-8'))
            self.assertEqual(0, run(report, '--force').returncode)
            self.assertEqual('pass', json.loads(report.read_text())['status'])
            report.unlink()
            self.assertEqual(0, run(report).returncode)
            self.assertEqual(original, source.read_text(encoding='utf-8'))

    def test_arrow_head_longer_than_landing_segment_is_detected(self):
        report = audit_svg(drawing())
        self.assertEqual('warning', report['status'])
        self.assertEqual('arrowhead_over_bend', report['findings'][0]['code'])
        self.assertEqual(8, report['measurements'][0]['straight_run'])
        self.assertEqual(18, report['measurements'][0]['marker_extent'])

    def test_longer_landing_corridor_passes_without_hiding_arrow(self):
        self.assertEqual('pass', audit_svg(drawing('M 0 0 L 40 0 L 40 32'))['status'])

    def test_default_marker_size_scales_with_stroke(self):
        self.assertEqual(32, audit_svg(drawing(width='4'))['measurements'][0]['marker_extent'])

    def test_user_space_marker_size_does_not_scale_with_stroke(self):
        report = audit_svg(drawing(width='4', units='markerUnits="userSpaceOnUse"'))
        self.assertEqual(8, report['measurements'][0]['marker_extent'])
        self.assertEqual('pass', report['status'])

    def test_start_arrow_is_audited_in_reverse(self):
        tag = '<path d="M 0 0 L 8 0 L 8 50" stroke-width="2.25" marker-start="url(#a)"/>'
        report = audit_svg(drawing(tag=tag))
        self.assertEqual('start', report['findings'][0]['side'])
        self.assertEqual(8, report['findings'][0]['straight_run'])

    def test_diagonal_is_optional_not_a_universal_style_ban(self):
        svg = drawing('M 0 0 L 50 50')
        self.assertEqual('pass', audit_svg(svg)['status'])
        self.assertIn('non_orthogonal_segment', [f['code'] for f in audit_svg(svg, orthogonal=True)['findings']])

    def test_collinear_waypoints_and_subpixel_jitter_do_not_shorten_run(self):
        report = audit_svg(drawing('M 0 0 L 20 0 L 20 0.01 L 40 0.01'))
        self.assertEqual('pass', report['status'])
        self.assertGreater(report['measurements'][0]['straight_run'], 39)

    def test_curves_fail_closed_as_unaudited(self):
        self.assertEqual('review', audit_svg(drawing('M 0 0 C 2 2 5 5 8 8'))['status'])

    def test_transformed_edges_are_not_silently_passed(self):
        tag = '<g transform="scale(2)"><path d="M 0 0 L 50 0" marker-end="url(#a)"/></g>'
        self.assertEqual('review', audit_svg(drawing(tag=tag))['status'])

    def test_css_sizing_is_not_silently_passed(self):
        tag = '<path d="M 0 0 L 50 0" style="stroke-width:8" marker-end="url(#a)"/>'
        self.assertEqual('review', audit_svg(drawing(tag=tag))['status'])

    def test_unresolved_marker_requires_review(self):
        tag = '<line x1="0" y1="0" x2="50" y2="0" marker-end="url(#missing)"/>'
        self.assertEqual('review', audit_svg(drawing(tag=tag))['status'])

    def test_relative_line_commands_are_supported(self):
        self.assertEqual('pass', audit_svg(drawing('m 0 0 h 50 v 32'))['status'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
