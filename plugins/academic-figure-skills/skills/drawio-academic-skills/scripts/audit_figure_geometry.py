#!/usr/bin/env python3
"""Bounded, offline audit of an exported SVG and an explicit relation scene.

Supports flat rect/rounded rect, ellipse, polygon, embedded-image boxes and
M/L polylines. Other paint/transform/CSS geometry is review, never an implicit
pass. Actual text ink boxes must be measured after fonts load. No network.
"""
from __future__ import annotations
import argparse, hashlib, json, math, re
from pathlib import Path
from xml.etree import ElementTree as ET

VERSION='1.0'
EPS=1e-7
def digest(data): return hashlib.sha256(data if isinstance(data,bytes) else data.encode()).hexdigest()
def tag(e): return e.tag.rsplit('}',1)[-1]
def num(e,k,default=0):
    s=e.get(k,str(default))
    if not re.fullmatch(r'[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?',s): raise ValueError(f'unsupported length {k}={s}')
    v=float(s)
    if not math.isfinite(v): raise ValueError('nonfinite coordinate')
    return v
def area(p): return abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(p,p[1:]+p[:1])))/2
def signed(p): return sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(p,p[1:]+p[:1]))/2
def cross(a,b): return a[0]*b[1]-a[1]*b[0]
def sub(a,b): return (a[0]-b[0],a[1]-b[1])
def convex(p):
    v=[cross(sub(b,a),sub(c,b)) for a,b,c in zip(p,p[1:]+p[:1],p[2:]+p[:2])]
    return all(x>=-EPS for x in v) or all(x<=EPS for x in v)
def clip(p,q):
    out=list(p);orient=1 if signed(q)>=0 else -1
    for a,b in zip(q,q[1:]+q[:1]):
        inp=out;out=[]
        if not inp:break
        d=sub(b,a)
        def side(x):return orient*cross(d,sub(x,a))
        for x,y in zip(inp,inp[1:]+inp[:1]):
            sx,sy=side(x),side(y);ix,iy=sx>=-EPS,sy>=-EPS
            if ix:out.append(x)
            if ix!=iy:
                t=sx/(sx-sy);out.append((x[0]+t*(y[0]-x[0]),x[1]+t*(y[1]-x[1])))
    return out
def inside(p,q): return area(p)-area(clip(p,q))<1e-5
def point_segment(p,a,b):
    d=sub(b,a);l=d[0]**2+d[1]**2
    t=max(0,min(1,((p[0]-a[0])*d[0]+(p[1]-a[1])*d[1])/l)) if l else 0
    return math.dist(p,(a[0]+t*d[0],a[1]+t*d[1]))
def segment_distance(a,b,c,d):
    u,v=sub(b,a),sub(d,c);den=cross(u,v)
    if abs(den)>EPS:
        t,z=cross(sub(c,a),v)/den,cross(sub(c,a),u)/den
        if -EPS<=t<=1+EPS and -EPS<=z<=1+EPS:return 0
    return min(point_segment(a,c,d),point_segment(b,c,d),point_segment(c,a,b),point_segment(d,a,b))
def distance(p,q):
    if len(p)>2 and len(q)>2 and area(clip(p,q))>EPS:return 0
    ps=list(zip(p,p[1:]+p[:1])) if len(p)>2 else [(p[0],p[1])]
    qs=list(zip(q,q[1:]+q[:1])) if len(q)>2 else [(q[0],q[1])]
    return min(segment_distance(a,b,c,d) for a,b in ps for c,d in qs)
def rect(x,y,w,h):return [(x,y),(x+w,y),(x+w,y+h),(x,y+h)]
def path_points(raw,closed=False):
    parts=re.findall(r'[A-Za-z]|[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?',raw)
    if re.sub(r'[\s,]','',re.sub(r'[A-Za-z]|[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?','',raw)):raise ValueError('unparsed path')
    pts=[];i=0;cmd=None
    while i<len(parts):
        if parts[i].isalpha():cmd=parts[i];i+=1
        if cmd in ('Z','z'):
            if not closed or i!=len(parts):raise ValueError('unsupported close')
            break
        if cmd not in ('M','L'):raise ValueError('only absolute M/L paths supported')
        if i+1>=len(parts) or parts[i].isalpha() or parts[i+1].isalpha():raise ValueError('incomplete path')
        pts.append((float(parts[i]),float(parts[i+1])));i+=2;cmd='L'
    if len(pts)<(3 if closed else 2):raise ValueError('too few points')
    if not all(math.isfinite(v) for p in pts for v in p):raise ValueError('nonfinite path')
    return pts
def poly(e):
    k=tag(e)
    if k in ('rect','image'):
        x,y,w,h=[num(e,v) for v in ('x','y','width','height')]
        if w<=0 or h<=0:raise ValueError('nonpositive box')
        rx=min(num(e,'rx'),w/2);ry=min(num(e,'ry',rx),h/2)
        if not rx or not ry:return rect(x,y,w,h)
        p=[]
        for cx,cy,start in [(x+w-rx,y+ry,-90),(x+w-rx,y+h-ry,0),(x+rx,y+h-ry,90),(x+rx,y+ry,180)]:
            for j in range(17):
                a=math.radians(start+90*j/16);p.append((cx+rx*math.cos(a),cy+ry*math.sin(a)))
        return p
    if k=='ellipse':
        cx,cy,rx,ry=[num(e,v) for v in ('cx','cy','rx','ry')]
        if rx<=0 or ry<=0:raise ValueError('bad ellipse')
        # Circumscribed regular polygon: conservative outer approximation.
        return [(cx+rx*math.cos(2*math.pi*j/96)/math.cos(math.pi/96),cy+ry*math.sin(2*math.pi*j/96)/math.cos(math.pi/96)) for j in range(96)]
    if k=='polygon':
        vals=[float(x) for x in re.split(r'[\s,]+',e.get('points','').strip()) if x]
        if len(vals)%2:raise ValueError('odd polygon coordinates')
        p=list(zip(vals[::2],vals[1::2]))
    elif k=='path':p=path_points(e.get('d',''),closed=True)
    else:raise ValueError(f'unsupported node {k}')
    if len(p)<3 or not convex(p):raise ValueError('only convex filled paths/polygons supported')
    return p
def line(e):
    if tag(e)=='line':return [(num(e,'x1'),num(e,'y1')),(num(e,'x2'),num(e,'y2'))]
    if tag(e)=='polyline':
        v=[float(x) for x in re.split(r'[\s,]+',e.get('points','').strip()) if x]
        if len(v)%2:raise ValueError('odd polyline')
        return list(zip(v[::2],v[1::2]))
    if tag(e)=='path':return path_points(e.get('d',''))
    raise ValueError('unsupported connector')
def audit_svg(source,scene,metrics=None):
    findings=[];coverage={};root=ET.fromstring(source);sha=digest(source)
    def issue(code,*ids,severity='error',**data):findings.append(dict(code=code,objects=list(ids),severity=severity,**data))
    if scene.get('schema_version')!=VERSION:issue('scene_version',severity='review')
    if scene.get('svg_sha256')!=sha:issue('stale_scene',severity='review')
    ids={};parent={c:e for e in root.iter() for c in e}
    for el in root.iter():
        if el.get('id'):
            if el.get('id') in ids:issue('duplicate_svg_id',el.get('id'),severity='review')
            ids[el.get('id')]=el
    def defined(el):
        while el is not None:
            if tag(el)=='defs':return True
            el=parent.get(el)
        return False
    def supported(el):
        a=el
        while a is not None:
            style=a.get('style')
            safe_color=style is not None and re.fullmatch(r'\s*color\s*:\s*#[0-9a-fA-F]{6}\s*;?\s*',style)
            if any(a.get(k) for k in ['transform','filter','clip-path','mask','class']) or (style and not safe_color):raise ValueError('transformed/styled/filtered/clipped geometry requires review')
            a=parent.get(a)
    def inherited(el,key,default):
        a=el
        while a is not None:
            if a.get(key) not in (None,'inherit'):return a.get(key)
            a=parent.get(a)
        return default
    def stroke_width(el):
        value=float(inherited(el,'stroke-width','1'))
        if not math.isfinite(value) or value<0:raise ValueError('bad inherited stroke width')
        return value
    if any(tag(x)=='style' for x in root.iter()):issue('stylesheet_not_audited',severity='review')
    vb=[float(x) for x in root.get('viewBox','').split()]
    if len(vb)!=4 or vb[2]<=0:raise ValueError('SVG needs a positive viewBox')
    width=scene.get('width_mm');clear=scene.get('min_clearance_pt',.8)
    if not isinstance(width,(float,int)) or width<=0 or not isinstance(clear,(float,int)) or clear<=0:raise ValueError('positive physical width/clearance required')
    scale=width*72/25.4/vb[2];pad=clear/scale
    nodes={};mapped=set();labeldefs=scene.get('labels',[]);edges=scene.get('edges',[])
    for sid in scene.get('backgrounds',[]):
        el=ids.get(sid)
        if el is None or parent.get(el) is not root or tag(el)!='rect' or el.get('width')!='100%' or el.get('height')!='100%' or el.get('fill','').lower() not in ('#ffffff','#fff','white') or el.get('stroke','none')!='none' or el.get('style') or el.get('transform') or num(el,'x')!=0 or num(el,'y')!=0:
            issue('invalid_canvas_background',str(sid),severity='review')
        else:mapped.add(sid)
    for n in scene.get('nodes',[]):
        try:
            if n['id'] in nodes:
                issue('duplicate_node_id',n['id'],severity='review');continue
            el=ids[n['svg_id']];supported(el);mapped.add(n['svg_id'])
            anchor=n.get('anchor')
            if anchor is not None:
                if tag(el)!='text':raise ValueError('virtual anchors require an actual text object')
                shape=rect(*[float(anchor[k]) for k in ('x','y','width','height')]);stroke=0
            else:shape=poly(el);stroke=stroke_width(el) if inherited(el,'stroke','none')!='none' else 0
            nodes[n['id']]=dict(poly=shape,stroke=stroke,svg_id=n['svg_id'],painted=anchor is None)
        except (ValueError,KeyError) as ex:issue('node_not_audited',n.get('id'),severity='review',reason=str(ex))
    allowed={};parents={}
    for r in scene.get('allowed_relations',[]):
        a,b=r.get('a'),r.get('b');kind=r.get('kind')
        if a not in nodes or b not in nodes or kind not in ('contains','overlap') or not r.get('reason'):
            issue('invalid_overlap_exception',str(a),str(b),severity='review');continue
        key=frozenset([a,b])
        if key in allowed:issue('duplicate_overlap_exception',a,b,severity='review')
        allowed[key]=kind
        if kind=='contains':
            if not inside(nodes[b]['poly'],nodes[a]['poly']):issue('declared_child_outside_parent',a,b)
            parents.setdefault(b,set()).add(a)
    def ancestors(n,trail=()):
        if n in trail:raise ValueError('containment cycle')
        result=set()
        for q in parents.get(n,[]):result.add(q);result.update(ancestors(q,trail+(n,)))
        return result
    ancestry={n:ancestors(n) for n in nodes}
    def related(a,b):return a==b or a in ancestry.get(b,set()) or b in ancestry.get(a,set())
    for i,(a,A) in enumerate(nodes.items()):
        for b,B in list(nodes.items())[i+1:]:
            if not A['painted'] or not B['painted']:continue
            if related(a,b) or frozenset([a,b]) in allowed:continue
            d=distance(A['poly'],B['poly']);need=(A['stroke']+B['stroke'])/2
            if area(clip(A['poly'],B['poly']))>EPS:issue('node_overlap',a,b)
            elif d+EPS<need+pad:issue('node_clearance',a,b,clearance_pt=(d-need)*scale)
    visible_text=[el for el in root.iter() if tag(el)=='text' and not defined(el) and ''.join(el.itertext()).replace('\u200b','').strip()]
    boxes={};audited_text=set();label_ids=set();validmetrics=metrics is not None and metrics.get('svg_sha256')==sha and metrics.get('fonts_ready') is True
    if (labeldefs or visible_text) and not validmetrics:issue('text_metrics_missing_or_stale',severity='review')
    metricboxes=metrics.get('boxes',{}) if validmetrics else {}
    for l in labeldefs:
        sid=l.get('svg_id');mapped.add(sid)
        try:
            label_id=l.get('id')
            if not isinstance(label_id,str) or not label_id.strip():raise ValueError('label ID must be a nonempty string')
            if label_id in label_ids:
                issue('duplicate_label_id',label_id,severity='review');continue
            label_ids.add(label_id)
            el=ids[sid];supported(el)
            if tag(el)!='text':raise ValueError('label requires an actual text object')
            txt=''.join(el.itertext()).replace('\u200b','').strip()
            if not txt:continue
            b=metricboxes[sid];x,y,w,h=[float(b[k]) for k in ('x','y','width','height')]
            if w<=0 or h<=0:raise ValueError('empty visible ink bounds')
            boxes[label_id]=dict(poly=rect(x,y,w,h),owner=l.get('owner'),svg_id=sid)
            audited_text.add(sid)
        except (ValueError,KeyError) as ex:issue('label_not_audited',l.get('id'),severity='review',reason=str(ex))
    for el in visible_text:
        if el.get('id') not in audited_text:issue('visible_text_not_audited',el.get('id','(no id)'),severity='review')
    for i,(a,A) in enumerate(boxes.items()):
        owner=A['owner']
        if owner in nodes and not inside(A['poly'],nodes[owner]['poly']):issue('label_outside_owner',a,owner)
        for b,B in nodes.items():
            if not B['painted']:continue
            if b==owner or b in ancestry.get(owner,set()):continue
            if distance(A['poly'],B['poly'])+EPS<B['stroke']/2+pad:issue('label_shape_collision',a,b)
        for b,B in list(boxes.items())[i+1:]:
            if distance(A['poly'],B['poly'])+EPS<pad:issue('label_collision',a,b)
    routes={};marker_count=0
    for edge in edges:
        i=edge.get('id');sid=edge.get('svg_id');mapped.add(sid)
        try:
            if i in routes:
                issue('duplicate_edge_id',i,severity='review');continue
            el=ids[sid];supported(el);pts=line(el);sw=stroke_width(el)
            if inherited(el,'marker-mid','none') not in ('none',''):
                issue('middle_marker_not_audited',i,severity='review')
            s,t=edge['source'],edge['target']
            if s not in nodes or t not in nodes:raise ValueError('unmapped endpoint')
            pts=[q for j,q in enumerate(pts) if not j or math.dist(q,pts[j-1])>EPS]
            if len(pts)<2:raise ValueError('zero-length edge')
            for endpoint,name in [(pts[0],s),(pts[-1],t)]:
                boundary=min(point_segment(endpoint,a,b) for a,b in zip(nodes[name]['poly'],nodes[name]['poly'][1:]+nodes[name]['poly'][:1]))
                if boundary>nodes[name]['stroke']/2+.1:issue('detached_endpoint',i,name,distance=boundary)
            routes[i]=(pts,s,t)
            for a,b in zip(pts,pts[1:]):
                for j,N in nodes.items():
                    if not N['painted']:continue
                    if related(j,s) or related(j,t):continue
                    if distance([a,b],N['poly'])+EPS<(sw+N['stroke'])/2:issue('edge_shape_collision',i,j)
                for j,L in boxes.items():
                    if distance([a,b],L['poly'])+EPS<sw/2+pad:issue('edge_label_collision',i,j)
            for side in ['start','end']:
                ref=inherited(el,'marker-'+side,'none')
                if not ref or ref=='none':continue
                marker_count+=1
                m=re.fullmatch(r'url\(#([^\s)]+)\)',ref)
                if not m or m[1] not in ids:raise ValueError('unresolved marker')
                marker=ids[m[1]]
                supported(marker)
                if marker.get('orient') not in ('auto','auto-start-reverse'):raise ValueError('fixed marker orientation')
                shapes=[q for q in marker if tag(q) in ('path','polygon')]
                if len(shapes)!=1:raise ValueError('one convex marker polygon required')
                supported(shapes[0])
                shape=poly(shapes[0]);v=[float(x) for x in marker.get('viewBox','').split()]
                if len(v)!=4 or min(v[2:])<=0:raise ValueError('marker viewBox')
                if marker.get('preserveAspectRatio','xMidYMid meet')!='xMidYMid meet':raise ValueError('marker aspect ratio')
                units=marker.get('markerUnits','strokeWidth')
                if units not in ('strokeWidth','userSpaceOnUse'):raise ValueError('marker units')
                k=min(num(marker,'markerWidth',3)/v[2],num(marker,'markerHeight',3)/v[3])*(sw if units=='strokeWidth' else 1)
                seq=pts if side=='end' else list(reversed(pts));end=seq[-1];d=sub(end,seq[-2]);run=math.hypot(*d);ux,uy=d[0]/run,d[1]/run
                rx,ry=num(marker,'refX'),num(marker,'refY')
                paint=[(end[0]+(x-rx)*k*ux-(y-ry)*k*uy,end[1]+(x-rx)*k*uy+(y-ry)*k*ux) for x,y in shape]
                extent=max((rx-x)*k for x,y in shape)
                # Collinear waypoints do not create a shorter landing corridor.
                for q in reversed(seq[:-2]):
                    vq=sub(end,q)
                    if abs(cross(vq,(ux,uy)))>.01 or vq[0]*ux+vq[1]*uy<run:break
                    run=vq[0]*ux+vq[1]*uy
                if run-extent-sw+EPS<pad:issue('arrow_clearance',i,side,remaining_pt=(run-extent-sw)*scale)
                target=t if side=='end' else s
                for j,N in nodes.items():
                    if not N['painted']:continue
                    if related(j,target):continue
                    if distance(paint,N['poly'])+EPS<(sw+N['stroke'])/2:issue('arrow_shape_collision',i,j)
                for j,L in boxes.items():
                    if distance(paint,L['poly'])+EPS<sw/2+pad:issue('arrow_label_collision',i,j)
        except (ValueError,KeyError,ZeroDivisionError) as ex:issue('edge_not_audited',i,severity='review',reason=str(ex))
    items=list(routes.items())
    for z,(i,(p,s,t)) in enumerate(items):
        for j,(q,u,v) in items[z+1:]:
            for a,b in zip(p,p[1:]):
                for c,d in zip(q,q[1:]):
                    if segment_distance(a,b,c,d)>EPS:continue
                    shared={s,t}&{u,v}
                    same=[x for x in (p[0],p[-1]) for y in (q[0],q[-1]) if math.dist(x,y)<.01]
                    den=cross(sub(b,a),sub(d,c))
                    if abs(den)>EPS:
                        z=cross(sub(c,a),sub(d,c))/den;at=(a[0]+z*(b[0]-a[0]),a[1]+z*(b[1]-a[1]))
                        if shared and any(math.dist(at,x)<.01 for x in same):continue
                    else:
                        key=0 if abs(b[0]-a[0])>=abs(b[1]-a[1]) else 1
                        overlap=min(max(a[key],b[key]),max(c[key],d[key]))-max(min(a[key],b[key]),min(c[key],d[key]))
                        if shared and overlap<=EPS and any(point_segment(x,a,b)<.01 and point_segment(x,c,d)<.01 for x in same):continue
                    issue('edge_intersection',i,j)
    geometry_tags={'rect','ellipse','circle','polygon','path','line','polyline','image','text','foreignObject','use'}
    for el in root.iter():
        if defined(el):continue
        if tag(el) in geometry_tags and el.get('id') not in mapped:issue('unmapped_visible_object',el.get('id','(no id)'),severity='review')
    # Deduplicate segment-level observations without hiding distinct object pairs.
    seen=set();unique=[]
    for f in findings:
        k=(f['code'],tuple(f['objects']),f.get('reason'))
        if k not in seen:seen.add(k);unique.append(f)
    status='fail' if any(x['severity']=='error' for x in unique) else 'review' if unique else 'pass'
    coverage.update(nodes_expected=len(scene.get('nodes',[])),nodes_checked=len(nodes),edges_expected=len(edges),edges_checked=len(routes),labels_expected=len(labeldefs),visible_labels_checked=len(boxes),marker_heads_checked=marker_count)
    if not nodes:status='review';unique.append(dict(code='empty_scene',objects=[],severity='review'))
    return dict(schema_version=VERSION,status=status,svg_sha256=sha,scene_sha256=digest(json.dumps(scene,sort_keys=True)),metrics_sha256=digest(json.dumps(metrics,sort_keys=True)) if metrics else None,coverage=coverage,findings=unique,
        scope='Bounded exported-SVG geometry; no scientific-meaning, renderer-parity or aesthetic certification.',min_clearance_pt=clear)

def audit_files(svg,scene,metrics=None):
    source=Path(svg).read_text();s=json.loads(Path(scene).read_text());m=json.loads(Path(metrics).read_text()) if metrics else None
    return audit_svg(source,s,m)
def verify_evidence(svg,evidence):
    """Replay current inputs instead of trusting a report's declared PASS."""
    try:
        stored=json.loads(Path(evidence['report']).read_text())
        current=audit_files(svg,evidence['scene'],evidence.get('text_metrics'))
        if stored!=current:return ['geometry report is stale or differs from replay']
        if current['status']!='pass':return ['geometry coverage/findings do not pass; inspect the geometry report']
        return []
    except (OSError,ValueError,KeyError,ET.ParseError) as ex:return ['geometry evidence unavailable: '+str(ex)]
def main():
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('svg',type=Path);a.add_argument('--scene',required=True,type=Path);a.add_argument('--text-metrics',type=Path);a.add_argument('--output',type=Path);a.add_argument('--force',action='store_true');args=a.parse_args()
    try:
        for q in [args.scene,args.text_metrics]:
            if q is not None and not q.is_file():raise ValueError(f'missing input {q}')
        if args.output:
            if any(args.output.resolve()==q.resolve() or (args.output.exists() and args.output.samefile(q)) for q in [args.svg,args.scene,args.text_metrics] if q is not None):raise ValueError('output aliases input')
            if args.output.exists() and not args.force:raise ValueError('refusing to overwrite report')
        r=audit_files(args.svg,args.scene,args.text_metrics)
        out=json.dumps(r,ensure_ascii=False,indent=2)+'\n'
        if args.output:args.output.write_text(out)
        else:print(out,end='')
        return 0 if r['status']=='pass' else 1 if r['status']=='fail' else 2
    except (ValueError,OSError,ET.ParseError,KeyError) as ex:a.exit(2,str(ex)+'\n')
if __name__=='__main__':raise SystemExit(main())
