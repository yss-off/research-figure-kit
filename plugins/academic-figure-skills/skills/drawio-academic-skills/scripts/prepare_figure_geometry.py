#!/usr/bin/env python3
"""Bind standalone base exports to stable semantic IDs without changing paint.

Bounded adapter for the sibling base's one-shape-per-node SVG export. Uses its
arch JSON and final drawio XML to verify counts/labels and obtain virtual text
anchors. Ambiguous or unsupported exports fail rather than guessing a mapping.
"""
import argparse,json,hashlib,re,html
from pathlib import Path
from xml.etree import ElementTree as E
from audit_figure_geometry import tag,digest

def prepare(svg,arch,drawio,relations,width_mm=182,clearance=.8):
    a=json.loads(Path(arch).read_text());r=E.fromstring(Path(svg).read_text());d=E.parse(drawio).getroot()
    vertices=[x for x in d.iter('mxCell') if x.get('vertex')=='1']
    texts=[x for x in r if tag(x)=='text'];connectors=[x for x in r if tag(x) in ('path','line','polyline')]
    shapes=[x for x in r if tag(x) in ('rect','polygon','ellipse','image')]
    backgrounds=[x for x in shapes if tag(x)=='rect' and x.get('width')=='100%' and x.get('height')=='100%' and x.get('fill','').lower() in ('#ffffff','#fff','white') and x.get('stroke','none')=='none' and not x.get('style') and not x.get('transform') and x.get('x','0')=='0' and x.get('y','0')=='0']
    if len(backgrounds)>1:raise ValueError('multiple canvas backgrounds')
    for x in backgrounds:shapes.remove(x);x.set('id','canvas-background')
    if len(a['nodes'])!=len(vertices) or len(texts)!=len(vertices):raise ValueError('ambiguous node/text inventory')
    if len(a['edges'])!=len(connectors):raise ValueError('ambiguous edge inventory; general stencils need a dedicated mapping')
    expected=sum(x['type']!='text' for x in a['nodes'])
    if len(shapes)!=expected:raise ValueError('ambiguous shape inventory; do not guess mapping')
    ns=[];ls=[];es=[];pos=0
    for n,v,t in zip(a['nodes'],vertices,texts):
        native=html.unescape(re.sub(r'<br\s*/?>','\n',v.get('value',''),flags=re.I)).replace('\r\n','\n')
        if native!=n['label'].replace('\r\n','\n'):raise ValueError('arch/native label order differs')
        tid='ink-'+n['id'];t.set('id',tid);ls.append(dict(id=n['id']+'-label',svg_id=tid,owner=n['id']))
        if n['type']=='text':
            g=v.find('mxGeometry');b={k:float(g.get(k)) for k in ('x','y','width','height')}
            ns.append(dict(id=n['id'],svg_id=tid,anchor=b))
        else:
            sh=shapes[pos];pos+=1;sid='shape-'+n['id'];sh.set('id',sid);ns.append(dict(id=n['id'],svg_id=sid))
    for n,el in zip(a['edges'],connectors):
        sid='edge-'+n['id'];el.set('id',sid)
        es.append(dict(id=n['id'],svg_id=sid,source=n.get('from',n.get('source')),target=n.get('to',n.get('target'))))
    E.register_namespace('','http://www.w3.org/2000/svg')
    data=E.tostring(r,encoding='unicode')
    scene=dict(schema_version='1.0',svg_sha256=digest(data),width_mm=width_mm,min_clearance_pt=clearance,nodes=ns,labels=ls,edges=es,allowed_relations=relations,
        backgrounds=['canvas-background'] if backgrounds else [],input_arch_sha256=hashlib.sha256(Path(arch).read_bytes()).hexdigest(),input_native_sha256=hashlib.sha256(Path(drawio).read_bytes()).hexdigest())
    return data,scene
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('svg',type=Path);p.add_argument('--arch',required=True,type=Path);p.add_argument('--drawio',required=True,type=Path);p.add_argument('--relations',required=True,type=Path);p.add_argument('--output-svg',required=True,type=Path);p.add_argument('--output-scene',required=True,type=Path);p.add_argument('--width-mm',type=float,default=182);p.add_argument('--clearance-pt',type=float,default=.8);a=p.parse_args()
    try:
        inputs=[a.svg,a.arch,a.drawio,a.relations]
        if a.output_svg.resolve()==a.output_scene.resolve():raise ValueError('output SVG and scene must be distinct files')
        for q in [a.output_svg,a.output_scene]:
            if q.exists() or any(q.resolve()==x.resolve() for x in inputs):raise ValueError('outputs must be new files and must not alias inputs')
        data,scene=prepare(a.svg,a.arch,a.drawio,json.loads(a.relations.read_text()),a.width_mm,a.clearance_pt)
        a.output_svg.write_text(data);a.output_scene.write_text(json.dumps(scene,indent=2))
    except (OSError,ValueError,KeyError,E.ParseError) as ex:p.exit(2,str(ex)+'\n')
if __name__=='__main__':main()
