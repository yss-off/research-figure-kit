// Invoke in an already-rendered local SVG page: await measureFigureInk(scene).
// No server/provider is required. getBBox is in SVG units for supported flat SVG.
async function measureFigureInk(scene) {
  await document.fonts.ready;
  const boxes = {};
  for (const label of scene.labels) {
    const el = document.getElementById(label.svg_id);
    if (!el || el.tagName.toLowerCase() !== 'text') throw Error('Missing text ' + label.svg_id);
    const b = el.getBBox();
    boxes[label.svg_id] = {x:b.x,y:b.y,width:b.width,height:b.height};
  }
  return {svg_sha256:scene.svg_sha256,fonts_ready:document.fonts.status === 'loaded',boxes,
    renderer:navigator.userAgent,scope:'Actual SVG text ink; no semantic or aesthetic verdict'};
}
