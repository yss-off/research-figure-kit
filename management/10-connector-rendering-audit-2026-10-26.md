# Exported arrow reliability audit — 2026-10-26

## Observed failure

A three-lane workflow's schema/XML and crossing checks passed, but two exported
arrows had only 16 and 8 SVG units of straight landing space for 18-unit marker
viewports. The heads straddled the final bend. This is a source-geometry and
review gap; successful manifest/crossing checks were insufficient evidence.
The regression fixtures use synthetic coordinates and contain no client figure.

## Base backend finding (not patched here)

Bundled upstream: `bahayonghang/drawio-skills` v2.7.0, pinned commit
`27dac02ce3b4901c844aaa623ad64c3d577c3a72`.

- `drawio/scripts/svg/drawio-to-svg.js:buildMarkerDefs`: open markers use an
  8-by-8 viewport and default SVG markerUnits (strokeWidth).
- `renderEdge` selects marker type but does not read `endSize`/`startSize`.
- Changing only XML `endSize=4` to `endSize=24` produces identical visible standalone
  SVG geometry (the embedded source metadata differs) in the local reproduction. This does not establish native Desktop behavior.
- Source and installed-cache renderer hashes matched during this audit:
  `974a05cfea7ec1ce02a3f18ddc5b8540cb25483986ebc76add48672954bc4ba6`.
- Remote upstream source retrieval failed in the available web tool, so no claim
  is made about a newer upstream fix. No external issue was posted.

Minimal reproduction: two rectangle vertices at (0,0,40,40) and (120,0,40,40),
a source/target-bound open-arrow edge with strokeWidth=2.25. Export it through
`drawioToSvg` twice, changing only `endSize`. Compare visible SVG/marker definitions after excluding embedded source metadata.
For the landing-space failure, a polyline `M 0 0 L 40 0 L 40 8` with markerWidth=8,
viewBox `0 0 10 10`, refX=10 and stroke-width=2.25 reproduces the over-bend head.

## Feedback implemented in the overlay

- Added a read-only exported SVG connector audit with conservative marker
  footprint measurement, optional orthogonal-path checks and explicit unaudited
  statuses for unsupported geometry.
- Added regression coverage for the failure and a longer-corridor repair,
  strokeWidth scaling, userSpaceOnUse, start markers, subpixel jitter, CSS,
  transforms and curves.
- Linked focused connector guidance from the skill and semantic-layout gates.
- Included connector regressions in the existing overlay smoke suite.

The pinned base runtime is unchanged. Runtime-cache installation, version bump,
commit, push and publication are outside this local source-feedback change.
