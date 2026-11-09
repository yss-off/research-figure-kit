"""Delivery boundary and revision regressions; no model-accuracy claim."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from figure_delivery import delivery_report, revision_impact
from figure_manifest import hydrate_artifacts, manifest_skeleton, validate_manifest
from figure_review import review_skeleton
from test_figure_review import completed_review, bind_review


class FigureDeliveryTests(unittest.TestCase):
    def setUp(self):
        from smoke_test import accepted_manifest
        self.tmp = tempfile.TemporaryDirectory()
        self.work = Path(self.tmp.name)
        self.svg = self.work / 'figure.svg'
        self.drawio = self.work / 'figure.drawio'
        self.svg.write_text("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 140 100'><rect id='input' x='0' y='0' width='20' height='20'/><rect id='output' x='80' y='0' width='20' height='20'/><rect id='support' x='0' y='60' width='100' height='20'/><line id='flow' x1='20' y1='10' x2='80' y2='10'/></svg>")
        self.drawio.write_text('<mxfile/>')
        self.doc = hydrate_artifacts(accepted_manifest(self.drawio, self.svg))
        self.doc['qa']['publication']['checks'] = ['Synthetic preview-format check; no venue claim']
        self.previous = completed_review(self.doc)
        bind_review(self.doc, self.previous, self.work / 'complete.review.json')

    def tearDown(self):
        self.tmp.cleanup()

    def test_complete_fixture_reports_evidence_not_certification(self):
        report = delivery_report(self.doc)
        self.assertEqual('evidence_complete', report['status'])
        self.assertTrue(all(x['status'] == 'evidence_checked' for x in report['layers'].values()))

    def test_geometry_pass_without_review_cannot_become_overall_pass(self):
        self.doc['qa'].pop('review')
        report = delivery_report(self.doc)
        self.assertEqual('evidence_checked', report['layers']['geometry']['status'])
        self.assertEqual('not_checked', report['layers']['readability']['status'])
        self.assertEqual('needs_review', report['status'])

    def test_geometry_failure_does_not_hide_independent_evidence_errors(self):
        for geometry in ({}, {**self.doc['qa']['geometry'], 'report': str(self.work / 'missing.json')}):
            with self.subTest(geometry=geometry):
                doc = copy.deepcopy(self.doc)
                doc['qa']['geometry'] = geometry
                doc['qa']['scientific']['svg_sha256'] = '0' * 64
                doc['qa']['scientific']['sources'][0]['sha256'] = '0' * 64
                doc['qa']['visual']['sha256'] = '0' * 64
                report = delivery_report(doc)
                codes = {item['code'] for item in report['findings']}
                self.assertTrue({'scientific_review_incomplete', 'scientific_source_stale',
                                 'visual_review_stale'} <= codes)
                self.assertEqual('review', report['layers']['scientific']['status'])
                self.assertEqual('review', report['layers']['readability']['status'])
                self.assertEqual('needs_review', report['status'])
                self.assertEqual(validate_manifest(doc, strict=True)['findings'], report['findings'])

    def test_unavailable_visual_file_does_not_skip_scientific_checks(self):
        doc = copy.deepcopy(self.doc)
        doc['qa']['visual']['artifact'] = str(self.work / 'missing.png')
        doc['qa']['scientific']['sources'][0]['sha256'] = '0' * 64
        report = delivery_report(doc)
        self.assertIn('scientific_source_stale', {f['code'] for f in report['findings']})
        self.assertNotEqual('evidence_checked', report['layers']['readability']['status'])

    def test_pdf_and_png_delivery_keep_diagnostic_geometry_svg(self):
        from _common import sha256_file
        for delivery_class, role in [('vector-submission', 'pdf'), ('raster-publication', 'png')]:
            with self.subTest(delivery_class=delivery_class):
                doc = copy.deepcopy(self.doc)
                primary = self.work / f'synthetic-primary.{role}'
                primary.write_bytes(b'Synthetic evidence-contract fixture; not publication content')
                doc['contract']['delivery_class'] = delivery_class
                doc['contract']['review_width_mm'] = 182
                doc['render']['artifacts'] = [a for a in doc['render']['artifacts'] if a['role'] != 'svg']
                doc['render']['artifacts'].append({'role': role, 'path': str(primary),
                                                  'evidence_label': 'recorded-fixture'})
                hydrate_artifacts(doc)
                doc['qa']['visual'].update(artifact=str(primary), sha256=sha256_file(primary))
                bind_review(doc, completed_review(doc), self.work / f'{role}.review.json')
                report = delivery_report(doc)
                self.assertEqual('evidence_complete', report['status'], report['findings'])

    def test_missing_publication_checks_are_not_inferred_from_pass_flag(self):
        self.doc['qa']['publication']['checks'] = []
        report = delivery_report(self.doc)
        self.assertEqual('not_checked', report['layers']['publication']['status'])
        self.assertEqual('needs_review', report['status'])

    def test_empty_or_failed_publication_entries_do_not_count(self):
        for checks in ([None], [' '], [{}], [True], ['Checked export', None],
                       [{'name': 'fonts', 'status': 'blocked', 'evidence': 'missing'}]):
            self.doc['qa']['publication']['checks'] = checks
            report = delivery_report(self.doc)
            self.assertEqual('needs_review', report['status'], checks)
            self.assertNotEqual('evidence_checked', report['layers']['publication']['status'])

    def test_structured_publication_checks_require_evidence(self):
        self.doc['qa']['publication']['checks'] = [
            {'name': 'preview format', 'status': 'pass', 'evidence': 'Inspected SVG preview'}]
        self.assertEqual('evidence_complete', delivery_report(self.doc)['status'])
        self.doc['qa']['publication']['checks'][0]['evidence'] = ''
        self.assertEqual('needs_review', delivery_report(self.doc)['status'])

    def test_strict_and_delivery_share_evidence_decisions(self):
        cases = [None, [], 'checked', [None], [' '], [{}], [True],
                 ['Checked export', None],
                 [{'name': 'fonts', 'status': 'blocked', 'evidence': 'missing'}],
                 [{'name': 'fonts', 'status': 'pass', 'evidence': ''}],
                 ['Inspected preview export'],
                 [{'name': 'fonts', 'status': 'pass', 'evidence': 'Inspected preview'}]]
        for checks in cases:
            with self.subTest(checks=checks):
                doc = copy.deepcopy(self.doc)
                doc['qa']['publication']['checks'] = checks
                strict = validate_manifest(doc, strict=True, verify_artifacts=True)
                delivery = delivery_report(doc)
                valid = checks in cases[-2:]
                self.assertEqual('pass' if valid else 'fail', strict['status'])
                self.assertEqual(strict['status'], delivery['validation_status'])
                self.assertEqual(strict['findings'], delivery['findings'])
                self.assertEqual(valid, delivery['status'] == 'evidence_complete')
        for layer in ('deterministic', 'publication'):
            for status in ('review', 'fail', 'blocked', 'pending', 'not_checked'):
                with self.subTest(layer=layer, status=status):
                    doc = copy.deepcopy(self.doc)
                    doc['qa'][layer]['status'] = status
                    strict = validate_manifest(doc, strict=True)
                    self.assertEqual('fail', strict['status'])
                    self.assertEqual(strict['findings'], delivery_report(doc)['findings'])

    def test_draft_warns_but_accepted_requires_publication_evidence(self):
        for missing in (True, False):
            doc = copy.deepcopy(self.doc)
            if missing:
                doc['qa']['publication'].pop('checks')
            else:
                doc['qa']['publication']['checks'] = [None]
            doc['status'] = 'review'
            draft = validate_manifest(doc)
            self.assertEqual('review', draft['status'])
            self.assertTrue(any(f['path'].startswith('qa.publication.checks')
                                and f['severity'] == 'warning' for f in draft['findings']))
            doc['status'] = 'accepted'
            self.assertEqual('fail', validate_manifest(doc)['status'])

    def test_both_cli_entries_reject_incomplete_publication(self):
        manifest = self.work / 'manifest.json'
        for checks, valid in ((['Inspected preview'], True), ([None], False), ([], False)):
            self.doc['qa']['publication']['checks'] = checks
            manifest.write_text(json.dumps(self.doc))
            before = manifest.read_bytes()
            validation = subprocess.run([sys.executable, str(ROOT / 'scripts/figure_manifest.py'),
                'validate', str(manifest), '--strict'], capture_output=True, text=True)
            delivery = subprocess.run([sys.executable, str(ROOT / 'scripts/figure_delivery.py'),
                str(manifest), '--strict'], capture_output=True, text=True)
            self.assertEqual(0 if valid else 2, validation.returncode, validation.stderr)
            self.assertEqual(0 if valid else 1, delivery.returncode, delivery.stderr)
            self.assertEqual(json.loads(validation.stdout)['findings'],
                             json.loads(delivery.stdout)['findings'])
            self.assertEqual(before, manifest.read_bytes())

    def test_malformed_previous_context_returns_clean_cli_error(self):
        manifest = self.work / 'manifest.json'
        manifest.write_text(json.dumps(self.doc))
        previous = self.work / 'previous.json'
        for context in ({}, {'contract': [], 'semantic_inventory': []}):
            record = copy.deepcopy(self.previous); record['context'] = context
            previous.write_text(json.dumps(record))
            run = subprocess.run([sys.executable, str(ROOT / 'scripts/figure_delivery.py'),
                str(manifest), '--previous-review', str(previous)], capture_output=True, text=True)
            self.assertEqual(2, run.returncode)
            self.assertNotIn('Traceback', run.stderr)

    def test_diagnostic_manifest_still_runs_strict_checks(self):
        self.doc['status'] = 'review'
        bind_review(self.doc, review_skeleton(self.doc), self.work / 'pending.review.json')
        self.assertEqual('needs_review', delivery_report(self.doc)['status'])

    def test_changed_caption_or_export_invalidates_evidence(self):
        self.doc['contract']['caption'] = 'New meaning'
        report = delivery_report(self.doc)
        self.assertEqual('needs_review', report['status'])
        self.assertIn('review_context_stale', {x['code'] for x in report['findings']})
        self.doc['contract']['caption'] = self.previous['context']['contract']['caption']
        self.svg.write_text(self.svg.read_text().replace("x='80'", "x='90'"))
        stale = validate_manifest(self.doc, strict=True, verify_artifacts=True)
        delivery = delivery_report(self.doc)
        self.assertEqual('fail', stale['status'])
        self.assertEqual(stale['findings'], delivery['findings'])
        self.assertEqual('needs_review', delivery['status'])

    def test_open_issue_hidden_from_visual_array_is_not_lost(self):
        r = copy.deepcopy(self.previous)
        r['issues'] = [{'id': 'query-identity', 'object_ids': ['input'], 'category': 'scientific',
            'problem': 'Identity omitted', 'evidence': 'Unlabelled input',
            'events': [{'state': 'open', 'decision': 'Repair', 'verification': '',
                'context_sha256': '0' * 64, 'artifacts': []}]}]
        bind_review(self.doc, r, self.work / 'issue.review.json')
        report = delivery_report(self.doc)
        self.assertEqual('needs_review', report['status'])
        self.assertIn('review_issue_unresolved', {x['code'] for x in report['findings']})
        self.assertEqual('query-identity', revision_impact(r, self.doc)['prior_issues'][0]['id'])

    def test_semantic_change_and_geometry_only_change_are_distinct(self):
        self.assertFalse(revision_impact(self.previous, self.doc)['requires_new_round'])
        self.doc['semantic_inventory']['edges'][0]['target'] = 'support'
        diff = revision_impact(self.previous, self.doc)
        self.assertEqual(['flow'], diff['inventory']['edges']['changed'])
        self.doc['semantic_inventory']['edges'][0]['target'] = 'output'
        Path(self.doc['render']['canonical_spec']).write_text('changed geometry')
        diff = revision_impact(self.previous, self.doc)
        self.assertEqual([], diff['inventory']['edges']['changed'])
        self.assertIn('canonical_spec', diff['changed_context'])
        self.assertTrue(diff['requires_new_round'])

    def test_unknown_or_malformed_inputs_fail_closed(self):
        for doc in ({}, {'qa': []}, {'qa': {'geometry': []}}, {'contract': None}):
            self.assertEqual('needs_review', delivery_report(doc)['status'])
        doc = manifest_skeleton('empty', 'Empty', 'architecture')
        self.assertEqual('needs_review', delivery_report(doc)['status'])

    def test_cli_exit_codes_no_overwrite_and_no_input_mutation(self):
        manifest = self.work / 'manifest.json'
        manifest.write_text(json.dumps(self.doc))
        prior = manifest.read_bytes()
        cli = [sys.executable, str(ROOT / 'scripts/figure_delivery.py'), str(manifest)]
        good = subprocess.run(cli + ['--strict'], capture_output=True, text=True)
        self.assertEqual(0, good.returncode, good.stderr)
        self.doc['qa'].pop('review')
        manifest.write_text(json.dumps(self.doc)); prior = manifest.read_bytes()
        output = self.work / 'delivery.json'
        bad = subprocess.run(cli + ['--strict', '--output', str(output)], capture_output=True, text=True)
        self.assertEqual(1, bad.returncode, bad.stderr)
        self.assertEqual('needs_review', json.loads(output.read_text())['status'])
        again = subprocess.run(cli + ['--output', str(output)], capture_output=True, text=True)
        self.assertEqual(2, again.returncode)
        alias = subprocess.run(cli + ['--output', str(manifest)], capture_output=True, text=True)
        self.assertEqual(2, alias.returncode)
        self.assertEqual(prior, manifest.read_bytes())

    def test_self_consistent_wrong_claim_remains_a_known_limit(self):
        r = copy.deepcopy(self.previous)
        r['claims'][0]['statement'] = 'Deliberately false scientific statement'
        bind_review(self.doc, r, self.work / 'false.review.json')
        # The report verifies associations, not truth. Never turn this into a
        # passing semantic detector benchmark or a promise to eliminate misses.
        self.assertEqual('evidence_complete', delivery_report(self.doc)['status'])

    def test_reader_questions_cannot_be_satisfied_by_geometry_or_claims(self):
        self.doc['contract']['reader_questions'] = [{'id': 'identity',
            'question': 'What identity is attached to the input?', 'object_ids': ['input']}]
        r = completed_review(self.doc)
        bind_review(self.doc, r, self.work / 'questions.review.json')
        self.assertEqual('needs_review', delivery_report(self.doc)['status'])
        r['readback']['answers'] = [{'id': 'identity', 'observation': 'The input label identifies Input.', 'status': 'pass'}]
        bind_review(self.doc, r, self.work / 'answered.review.json')
        self.assertEqual('evidence_complete', delivery_report(self.doc)['status'])
        # A new round must never copy answers from the old figure.
        self.assertEqual([], review_skeleton(self.doc)['readback']['answers'])
        for mutate in ('duplicate', 'blank', 'unknown'):
            altered = copy.deepcopy(r)
            if mutate == 'duplicate': altered['readback']['answers'] *= 2
            if mutate == 'blank': altered['readback']['answers'][0]['observation'] = ' '
            if mutate == 'unknown': altered['readback']['answers'][0]['id'] = 'other'
            bind_review(self.doc, altered, self.work / f'{mutate}.review.json')
            self.assertEqual('needs_review', delivery_report(self.doc)['status'])


if __name__ == '__main__':
    unittest.main()
