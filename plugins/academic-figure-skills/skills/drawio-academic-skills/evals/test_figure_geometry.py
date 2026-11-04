"""Anonymous regressions for frame/arrow paint and evidence freshness."""
import copy,json,subprocess,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_figure_geometry import audit_svg,digest,verify_evidence
from prepare_figure_geometry import prepare

def drawing(parts,defs=''):
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">'+defs+parts+'</svg>'
def scene(svg,nodes,edges=(),allowed=(),labels=()):
    return dict(schema_version='1.0',svg_sha256=digest(svg),width_mm=182,min_clearance_pt=.8,nodes=[dict(id=n,svg_id=n) for n in nodes],edges=list(edges),labels=list(labels),allowed_relations=list(allowed))
def marker():return '<defs><marker id="m" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M 0 0 L 10 5 L 0 10 Z"/></marker></defs>'
class FigureGeometryTests(unittest.TestCase):
    def test_duplicate_scene_nodes_and_edges_cannot_hide_incomplete_coverage(self):
        svg = drawing('<rect id="a" x="0" y="0" width="20" height="30"/><rect id="b" x="200" y="0" width="20" height="30"/><line id="e" x1="20" y1="15" x2="200" y2="15"/>')
        original = scene(svg, ['a', 'b'], [dict(id='e', svg_id='e', source='a', target='b')])
        self.assertEqual('pass', audit_svg(svg, original)['status'])
        for kind, code in [('nodes', 'duplicate_node_id'), ('edges', 'duplicate_edge_id')]:
            with self.subTest(kind=kind):
                s = copy.deepcopy(original)
                s[kind].append(copy.deepcopy(s[kind][0]))
                result = audit_svg(svg, s)
                self.assertEqual('review', result['status'])
                self.assertIn(code, [x['code'] for x in result['findings']])

    def test_duplicate_label_ids_cannot_hide_overlapping_text(self):
        svg = drawing('<text id="a" x="0" y="20">first</text><text id="b" x="0" y="20">second</text>')
        s = scene(svg, [])
        s['nodes'] = [dict(id=n, svg_id=n, anchor=dict(x=0, y=0, width=100, height=30)) for n in ('a', 'b')]
        metrics = dict(svg_sha256=digest(svg), fonts_ready=True,
                       boxes={n: dict(x=0, y=5, width=40, height=20) for n in ('a', 'b')})
        s['labels'] = [dict(id=n+'-label', svg_id=n, owner=n) for n in ('a', 'b')]
        result = audit_svg(svg, s, metrics)
        self.assertEqual('fail', result['status'])
        self.assertIn('label_collision', [x['code'] for x in result['findings']])
        for duplicate in ('same', ''):
            with self.subTest(label_id=duplicate):
                s['labels'] = [dict(id=duplicate, svg_id=n, owner=n) for n in ('a', 'b')]
                result = audit_svg(svg, s, metrics)
                self.assertEqual('review', result['status'])
                self.assertIn('duplicate_label_id' if duplicate else 'label_not_audited',
                              [x['code'] for x in result['findings']])

    def test_middle_markers_require_review_unless_explicitly_disabled(self):
        nodes = '<rect id="a" x="0" y="0" width="20" height="30"/><rect id="b" x="200" y="0" width="20" height="30"/><rect id="obstacle" x="30" y="50" width="20" height="20"/>'
        line = '<polyline id="e" points="20,15 120,15 200,15" stroke="black" stroke-width="2.2" fill="none" {}/>'
        defs = marker().replace('markerWidth="8" markerHeight="8"', 'markerWidth="80" markerHeight="80"')
        variants = [(line.format('marker-mid="url(#m)"'), 'review'),
                    ('<g marker-mid="url(#m)"><g>' + line.format('marker-mid="inherit"') + '</g></g>', 'review'),
                    ('<g marker-mid="url(#m)">' + line.format('marker-mid="none"') + '</g>', 'pass'),
                    (line.format(''), 'pass')]
        for edge, expected in variants:
            with self.subTest(edge=edge):
                svg = drawing(nodes + edge, defs)
                result = audit_svg(svg, scene(svg, ['a', 'b', 'obstacle'], [dict(id='e', svg_id='e', source='a', target='b')]))
                self.assertEqual(expected, result['status'])
                self.assertEqual(expected == 'review', 'middle_marker_not_audited' in [x['code'] for x in result['findings']])

    def test_inherited_markers_match_explicit_paint_checks(self):
        nodes = '<rect id="a" x="0" y="0" width="20" height="30"/><rect id="b" x="80" y="0" width="20" height="30"/>'
        edges = [dict(id='e', svg_id='e', source='a', target='b')]
        for side in ('start', 'end'):
            for size in (8, 80):
                with self.subTest(side=side, size=size):
                    defs = marker().replace('markerWidth="8" markerHeight="8"', f'markerWidth="{size}" markerHeight="{size}"')
                    line = '<line id="e" x1="20" y1="15" x2="80" y2="15" stroke-width="2.2" {}/>'
                    attr = f'marker-{side}="url(#m)"'
                    explicit = drawing(nodes + line.format(attr), defs)
                    inherited = drawing(nodes + f'<g {attr}><g>' + line.format(f'marker-{side}="inherit"') + '</g></g>', defs)
                    results = [audit_svg(svg, scene(svg, ['a', 'b'], edges)) for svg in (explicit, inherited)]
                    self.assertEqual(results[0]['findings'], results[1]['findings'])
                    self.assertEqual(1, results[1]['coverage']['marker_heads_checked'])
                    self.assertEqual('pass' if size == 8 else 'fail', results[1]['status'])
                    if size == 80:
                        self.assertIn('arrow_clearance', [x['code'] for x in results[1]['findings']])
                    disabled = drawing(nodes + f'<g {attr}>' + line.format(f'marker-{side}="none"') + '</g>', defs)
                    result = audit_svg(disabled, scene(disabled, ['a', 'b'], edges))
                    self.assertEqual('pass', result['status'])
                    self.assertEqual(0, result['coverage']['marker_heads_checked'])

    def test_unsupported_or_unresolved_inherited_marker_requires_review(self):
        nodes = '<rect id="a" x="0" y="0" width="20" height="30"/><rect id="b" x="80" y="0" width="20" height="30"/>'
        edge = '<g marker-end="url(#m)"><line id="e" x1="20" y1="15" x2="80" y2="15"/></g>'
        for defs in ('', marker().replace('<marker ', '<marker transform="scale(2)" '),
                     marker().replace('<path ', '<path transform="scale(2)" ')):
            with self.subTest(defs=defs):
                svg = drawing(nodes + edge, defs)
                result = audit_svg(svg, scene(svg, ['a', 'b'], [dict(id='e', svg_id='e', source='a', target='b')]))
                self.assertEqual('review', result['status'])
                self.assertIn('edge_not_audited', [x['code'] for x in result['findings']])

    def test_text_anchors_cannot_bypass_label_coverage_or_measurement(self):
        for separated in (False, True):
            svg = drawing('<text id="a" x="0" y="20">first</text>' +
                          f'<text id="b" x="{100 if separated else 0}" y="20">second</text>')
            s = scene(svg, [])
            s['nodes'] = [dict(id=n, svg_id=n, anchor=dict(x=x, y=0, width=80, height=30))
                          for n, x in [('a', 0), ('b', 100 if separated else 0)]]
            metrics = dict(svg_sha256=digest(svg), fonts_ready=True, boxes={
                n: dict(x=x, y=5, width=40, height=20) for n, x in [('a', 0), ('b', 100 if separated else 0)]})
            labels = [dict(id=n+'-label', svg_id=n, owner=n) for n in ('a', 'b')]
            for declarations in ([], labels[:1], labels):
                s['labels'] = declarations
                with self.subTest(separated=separated, labels=len(declarations)):
                    result = audit_svg(svg, s)
                    self.assertEqual('review', result['status'])
                    self.assertIn('text_metrics_missing_or_stale', [x['code'] for x in result['findings']])
                    result = audit_svg(svg, s, metrics)
                    if len(declarations) < 2:
                        self.assertEqual('review', result['status'])
                        self.assertIn('visible_text_not_audited', [x['code'] for x in result['findings']])
                    else:
                        self.assertEqual('pass' if separated else 'fail', result['status'])
                        if not separated:
                            self.assertIn('label_collision', [x['code'] for x in result['findings']])

    def test_prepare_cli_rejects_aliased_outputs_before_writing(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            svg = p/'input.svg'; arch = p/'input.arch.json'; native = p/'input.drawio'; relations = p/'relations.json'
            svg.write_text(drawing('<rect x="0" y="0" width="80" height="30"/><text x="1" y="20">one</text>'))
            arch.write_text(json.dumps(dict(nodes=[dict(id='n', type='rect', label='one')], edges=[])))
            native.write_text('<mxfile><diagram><mxGraphModel><root><mxCell vertex="1" value="one"><mxGeometry x="0" y="0" width="80" height="30"/></mxCell></root></mxGraphModel></diagram></mxfile>')
            relations.write_text('[]')
            originals = {f: f.read_bytes() for f in (svg, arch, native, relations)}
            command = [sys.executable, str(Path(__file__).resolve().parents[1]/'scripts/prepare_figure_geometry.py'),
                       str(svg), '--arch', str(arch), '--drawio', str(native), '--relations', str(relations)]
            output = p/'output.svg'
            # Also exercise differently spelled paths resolving to the same file.
            (p/'sub').mkdir()
            for alias in (output, p/'sub/../output.svg'):
                result = subprocess.run(command + ['--output-svg', str(output), '--output-scene', str(alias)], capture_output=True, text=True)
                self.assertEqual(2, result.returncode, result.stderr)
                self.assertIn('distinct files', result.stderr)
                self.assertFalse(output.exists())
                self.assertTrue(all(f.read_bytes() == data for f, data in originals.items()))
            output_scene = p/'scene.json'
            result = subprocess.run(command + ['--output-svg', str(output), '--output-scene', str(output_scene)], capture_output=True, text=True)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertTrue(output.read_text().startswith('<svg'))
            self.assertEqual(digest(output.read_text()), json.loads(output_scene.read_text())['svg_sha256'])
            self.assertTrue(all(f.read_bytes() == data for f, data in originals.items()))

    def test_only_exact_root_canvas_can_be_a_background(self):
        svg=drawing('<rect id="canvas" width="100%" height="100%" fill="#FFFFFF"/><rect id="a" x="10" y="10" width="20" height="20"/>')
        s=scene(svg,['a']);s['backgrounds']=['canvas'];self.assertEqual('pass',audit_svg(svg,s)['status'])
        s['backgrounds']=['a'];self.assertNotEqual('pass',audit_svg(svg,s)['status'])
    def test_external_rectangle_over_sloped_frame_is_blocked(self):
        svg=drawing('<polygon id="frame" points="0,140 200,80 200,250 0,200"/><rect id="new" x="120" y="90" width="70" height="50"/>')
        r=audit_svg(svg,scene(svg,['frame','new']));self.assertEqual('fail',r['status']);self.assertIn('node_overlap',[x['code'] for x in r['findings']])
    def test_exact_child_containment_is_allowed_but_not_external_overlap(self):
        svg=drawing('<rect id="frame" x="0" y="0" width="200" height="200"/><rect id="child" x="20" y="20" width="40" height="40"/>')
        s=scene(svg,['frame','child'],allowed=[dict(kind='contains',a='frame',b='child',reason='actual local component')])
        self.assertEqual('pass',audit_svg(svg,s)['status'])
        bad=svg.replace('x="20" y="20"','x="180" y="180"');s['svg_sha256']=digest(bad)
        self.assertIn('declared_child_outside_parent',[x['code'] for x in audit_svg(bad,s)['findings']])
    def test_arrow_marker_crossing_unrelated_outline_is_blocked(self):
        # Centerline fits its final run, but the marker wing touches frame f.
        svg=drawing('<rect id="a" x="0" y="90" width="30" height="20"/><rect id="b" x="100" y="90" width="30" height="20"/><rect id="f" x="76" y="106" width="12" height="20"/><line id="e" x1="30" y1="100" x2="100" y2="100" stroke-width="2.2" marker-end="url(#m)"/>',marker())
        r=audit_svg(svg,scene(svg,['a','b','f'],[dict(id='e',svg_id='e',source='a',target='b')]))
        self.assertIn('arrow_shape_collision',[x['code'] for x in r['findings']])
    def test_arrow_fitting_length_can_still_lack_clearance(self):
        svg=drawing('<rect id="a" x="0" y="0" width="20" height="30"/><rect id="b" x="40" y="0" width="20" height="30"/><line id="e" x1="20" y1="15" x2="40" y2="15" stroke-width="2.2" marker-end="url(#m)"/>',marker())
        s=scene(svg,['a','b'],[dict(id='e',svg_id='e',source='a',target='b')]);s['width_mm']=30
        self.assertIn('arrow_clearance',[x['code'] for x in audit_svg(svg,s)['findings']])
    def test_corrected_spaced_arrow_passes(self):
        svg=drawing('<rect id="a" x="0" y="0" width="20" height="30"/><rect id="b" x="80" y="0" width="20" height="30"/><line id="e" x1="20" y1="15" x2="80" y2="15" stroke-width="2.2" marker-end="url(#m)"/>',marker())
        self.assertEqual('pass',audit_svg(svg,scene(svg,['a','b'],[dict(id='e',svg_id='e',source='a',target='b')]))['status'])
        colored=svg.replace('id="e"','id="e" style="color: #000000"')
        self.assertEqual('pass',audit_svg(colored,scene(colored,['a','b'],[dict(id='e',svg_id='e',source='a',target='b')]))['status'])
    def test_unmapped_curve_cannot_pass(self):
        svg=drawing('<rect id="a" x="0" y="0" width="20" height="30"/><path id="curve" d="M 30 0 C 40 0 50 0 60 10"/>')
        self.assertEqual('review',audit_svg(svg,scene(svg,['a']))['status'])
    def test_transforms_and_stale_scene_require_review(self):
        svg=drawing('<rect id="a" x="0" y="0" width="20" height="30" transform="translate(2)"/>')
        self.assertEqual('review',audit_svg(svg,scene(svg,['a']))['status'])
        simple=svg.replace(' transform="translate(2)"','');s=scene(simple,['a']);s['svg_sha256']='old'
        self.assertEqual('review',audit_svg(simple,s)['status'])
    def test_visible_text_requires_current_font_ink_and_checks_shape_collision(self):
        svg=drawing('<rect id="a" x="0" y="0" width="50" height="40"/><text id="t" x="40" y="20">test</text>')
        s=scene(svg,['a'],labels=[dict(id='label',svg_id='t')])
        self.assertEqual('review',audit_svg(svg,s)['status'])
        m=dict(svg_sha256=digest(svg),fonts_ready=True,boxes={'t':dict(x=40,y=10,width=30,height=20)})
        self.assertIn('label_shape_collision',[x['code'] for x in audit_svg(svg,s,m)['findings']])
    def test_source_container_does_not_exempt_marker_at_external_target(self):
        svg=drawing('<rect id="parent" x="0" y="0" width="100" height="150"/><rect id="a" x="20" y="100" width="20" height="20"/><rect id="b" x="140" y="10" width="20" height="20"/><line id="e" x1="40" y1="110" x2="140" y2="20" stroke-width="2.2" marker-end="url(#m)"/>',marker())
        s=scene(svg,['parent','a','b'],[dict(id='e',svg_id='e',source='a',target='b')],[dict(kind='contains',a='parent',b='a',reason='child')])
        self.assertEqual('pass',audit_svg(svg,s)['status'])
    def test_shared_source_does_not_hide_a_later_crossing(self):
        svg=drawing('<rect id="a" x="0" y="0" width="20" height="20"/><rect id="b" x="100" y="0" width="20" height="20"/><rect id="c" x="100" y="100" width="20" height="20"/><path id="e" d="M 20 10 L 80 10 L 80 110 L 100 110"/><path id="f" d="M 20 10 L 40 10 L 40 60 L 90 60 L 90 10 L 100 10"/>')
        es=[dict(id='e',svg_id='e',source='a',target='c'),dict(id='f',svg_id='f',source='a',target='b')]
        r=audit_svg(svg,scene(svg,['a','b','c'],es))
        self.assertIn('edge_intersection',[x['code'] for x in r['findings']])
    def test_replay_rejects_stale_or_forged_report(self):
        svg=drawing('<rect id="a" x="0" y="0" width="20" height="20"/>');s=scene(svg,['a'])
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'s.svg').write_text(svg);(p/'scene.json').write_text(json.dumps(s));r=audit_svg(svg,s)
            (p/'report.json').write_text(json.dumps(r));ev=dict(scene=str(p/'scene.json'),report=str(p/'report.json'))
            self.assertEqual([],verify_evidence(p/'s.svg',ev))
            (p/'s.svg').write_text(svg.replace('width="20"','width="21"'))
            self.assertTrue(verify_evidence(p/'s.svg',ev))
            r['status']='pass';r['findings']=[];(p/'report.json').write_text(json.dumps(r))
            self.assertTrue(verify_evidence(p/'s.svg',ev))
    def test_inherited_marker_width_is_not_treated_as_default(self):
        svg=drawing('<rect id="a" x="0" y="0" width="20" height="30"/><rect id="b" x="45" y="0" width="20" height="30"/><g stroke-width="4"><line id="e" x1="20" y1="15" x2="45" y2="15" marker-end="url(#m)"/></g>',marker())
        self.assertIn('arrow_clearance',[x['code'] for x in audit_svg(svg,scene(svg,['a','b'],[dict(id='e',svg_id='e',source='a',target='b')]))['findings']])
    def test_base_prepare_handles_canvas_and_br_without_guessing(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            (p/'s.svg').write_text(drawing('<rect width="100%" height="100%" fill="#FFFFFF"/><text>one<tspan>two</tspan></text>'))
            (p/'a.json').write_text(json.dumps(dict(nodes=[dict(id='n',type='text',label='one\ntwo')],edges=[])))
            (p/'d.drawio').write_text('<mxfile><diagram><mxGraphModel><root><mxCell vertex="1" value="one&lt;br&gt;two"><mxGeometry x="0" y="0" width="50" height="50"/></mxCell></root></mxGraphModel></diagram></mxfile>')
            svg,s=prepare(p/'s.svg',p/'a.json',p/'d.drawio',[])
            self.assertEqual(['canvas-background'],s['backgrounds']);self.assertEqual('ink-n',s['nodes'][0]['svg_id'])
            (p/'s.svg').write_text(drawing('<text>one</text><text>two</text>'))
            with self.assertRaises(ValueError):prepare(p/'s.svg',p/'a.json',p/'d.drawio',[])

if __name__=='__main__':unittest.main()
