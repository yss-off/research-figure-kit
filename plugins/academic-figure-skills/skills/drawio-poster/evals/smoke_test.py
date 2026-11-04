#!/usr/bin/env python3
"""Focused behavior tests; no network, font downloads, or rendering dependency."""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "poster_tools.py"
spec = importlib.util.spec_from_file_location("poster_tools", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

XML = '''<mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/>
<mxCell id="a" value="Main condition" style="fontSize=24" vertex="1" parent="1"/>
<mxCell id="b" value="A note" style="fontSize=16" vertex="1" parent="1"/>
<mxCell id="joint" value=" " vertex="1" parent="1"/></root></mxGraphModel>'''


class PosterTests(unittest.TestCase):
    def test_display_scale_changes_readability_result(self):
        bad = module.audit(XML, 1280, 432, {"a"}, {"b"})
        self.assertEqual(bad["status"], "review")
        self.assertEqual(bad["labels"][0]["display_font_px"], 8.1)
        self.assertEqual(len(bad["labels"]), 2)
        good = module.audit(XML, 640, 432, {"a"}, {"b"})
        self.assertEqual(good["status"], "clear")

    def test_missing_evidence_never_passes(self):
        self.assertEqual(module.audit(XML, 640, 432, set(), set())["status"], "review")
        self.assertEqual(module.audit(XML.replace('fontSize=24', ''), 640, 432, {"a"}, {"b"})["status"], "review")
        for width in (0, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                module.audit(XML, width, 432, {"a"}, {"b"})
        with self.assertRaises(ValueError):
            module.audit(XML, 640, 432, {"missing"}, set())
        with self.assertRaises(ValueError):
            module.audit(XML, 640, 432, {"a"}, {"a"})

    def test_compressed_multi_page_and_dtd_rejected(self):
        for xml in ('<mxfile><diagram>compressed</diagram></mxfile>',
                    '<mxfile><diagram>'+XML+'</diagram><diagram>'+XML+'</diagram></mxfile>',
                    '<!DOCTYPE x>'+XML):
            with self.assertRaises(ValueError):
                module.audit(xml, 640, 432, set(), set())

    def test_wrap_preserves_content_identifiers_and_protected_phrase(self):
        text = '甲乙我们订阅Plan20X备用'
        lines = module.wrap_text(text, len, 9, ['我们', '备用'])
        self.assertEqual(''.join(lines), text)
        self.assertTrue(all(len(x) <= 9 for x in lines))
        self.assertTrue(any('Plan20X' in x for x in lines))
        self.assertTrue(any('我们' in x for x in lines))

    def test_punctuation_and_explicit_paragraphs(self):
        lines = module.wrap_text('甲乙丙，丁（戊己）庚', len, 3)
        self.assertEqual(''.join(lines), '甲乙丙，丁（戊己）庚')
        self.assertTrue(all(not x.startswith(('，', '）')) and not x.endswith('（') for x in lines))
        self.assertEqual(module.wrap_text('甲乙\n\n丙丁', len, 8), ['甲乙', '', '丙丁'])
        with self.assertRaises(ValueError):
            module.wrap_text('Plan20X', len, 3)

    def test_audit_cli_reports_review_exit_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'poster.drawio'
            path.write_text(XML, encoding='utf-8')
            run = subprocess.run([sys.executable, str(SCRIPT), 'audit', str(path),
                                  '--source-width', '1280', '--display-width', '432',
                                  '--primary-ids', 'a', '--secondary-ids', 'b'], capture_output=True, text=True)
            self.assertEqual(run.returncode, 1)
            self.assertEqual(json.loads(run.stdout)['status'], 'review')


if __name__ == '__main__':
    unittest.main()
