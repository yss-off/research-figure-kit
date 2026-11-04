# Exported geometry and current evidence

This is a bounded geometry audit and a delivery-evidence check, not an automatic
judge of scientific correctness, beauty, publisher compliance or every SVG.
It applies to publication model/workflow figures; diagnostic previews remain
possible even when findings are unresolved.

## Prepare and measure

Give exported painted objects stable IDs and bind them to semantic node/edge IDs.
For the sibling base's one-shape-per-node standalone output, the offline helper
can prepare an identity-only derivative without changing paint:

```
python scripts/prepare_figure_geometry.py figure.svg --arch figure.arch.json \
  --drawio figure.drawio --relations allowed-relations.json \
  --output-svg figure.audit.svg --output-scene figure.scene.json
```

The helper verifies native/arch/text counts and labels. A different exporter or
complex stencil may require an explicit mapping; an ambiguous mapping fails
instead of guessing. Keep the final canonical file, mapped derivative and their
provenance. If the mapped SVG is delivered, list that same path in the manifest.

`allowed-relations.json` is an array of `{kind,a,b,reason}` objects. `contains`
requires the member's actual geometry to lie inside that specific parent;
`overlap` authorizes one specific intentional pair such as two grid strokes.
There are no global background/passive-node exemptions. A real pixel-decoder
container may contain its feature planes while an external upsampler still
must not overlap it. Declare intended containment before checking; never add an
exception solely to turn a real defect into PASS. Scientific changes remain
author-owned.

Render the exact mapped SVG with fonts loaded. The local browser function in
`scripts/measure_figure_ink.js` returns actual text-ink boxes for the scene.
It can run in any available local browser environment; no MCP server, network,
external model or specific provider is required. Save the returned JSON. Without
fresh text metrics, visible text is `not_audited`, never silently passed.

```
python scripts/audit_figure_geometry.py figure.audit.svg \
  --scene figure.scene.json --text-metrics figure.ink.json \
  --output figure.geometry.json
```

Reports bind SVG bytes, scene and ink measurements. They cover node collisions,
text ink, line paths, endpoints, marker paint polygons and marker landing
clearance. Clearance includes stroke widths and a configurable physical gap at
the declared final width. The default 0.8pt is a local QA heuristic, not an IEEE
or TWC rule. A marker fitting its last segment can still fail for touching an
unrelated sloped boundary. Source-container containment does not exempt an
arrowhead near an external target. Shared endpoints do not exempt later crossings.

Flat rectangles/rounded rectangles, ellipses, convex polygons, embedded-image
boxes and absolute M/L paths are supported. Ellipses and rounded corners use
bounded polygon approximations; review near-tangent cases. Unsupported curves,
CSS, transforms, clipping, unresolved markers, missing objects or stale metrics
produce `review` rather than PASS. Middle markers (`marker-mid`), including
inherited values, are not supported and also produce `review`; an explicit
`none` override disables that marker. Raster contents are outside geometry coverage:
their boxes are checked but their scientific meaning still needs source review.
Exit codes: 0 pass, 1 detected defect, 2 incomplete/unsupported evidence. Reports
are read-only to the input SVG and do not overwrite existing reports by default.

## Separate acceptance layers

Manifest 1.1 also requires `qa.review: {path, sha256, schema_version: "1.0"}`.
Follow [review-contract.md](review-contract.md) for claim/source coverage,
actual-artifact reading, persistent history, invalidation and legacy migration.
`qa.visual.issues` contains current unresolved issues, not closed history.
The existing geometry check is replayable, not merely a self-reported status;
the semantic and visual conclusions remain recorded reviewer judgments.

Keep at least these separate records:

- `qa.geometry`: paths `svg`, `scene`, `report`, optional `text_metrics`. The
  manifest checker replays inputs instead of trusting the stored status.
- `qa.visual`: `status: pass`, the actual reviewed `artifact`, its `sha256`,
  closed `issues` and a short record of viewing the exported PDF/PNG at size.
- `qa.scientific`: `status: pass`, current `svg_sha256`, a concrete `basis`, and
  `sources: [{path,sha256}]`. A static software diagram may cite its approved
  contract instead of empirical data; do not invent a data source. This is a
  recorded reviewer judgment, not machine verification of the source's meaning.

Accepted/strict manifest validation rejects missing, failing or stale evidence,
inventory IDs that differ from the geometry scene, unresolved visual findings,
and changed source files. Review/planning manifests remain usable for diagnostics.
Validation PASS still means its declared checks passed, not publisher acceptance.

For data-derived icons, use one traceable sample/approved construction and record
common axes, crops and display transformations. A schematic label is not permission
to invent protocol morphology or pair unrelated input/output masks. Scientific
review must distinguish a ground-truth example from measured model predictions.

## Regression discipline

Anonymous minimal fixtures must reject a rectangle crossing a sloped frame,
an arrowhead touching an unrelated shape, a too-tight but length-fitting marker,
and stale/unmapped geometry. Legitimate containment and a corrected spaced arrow
must pass. Run focused tests, then plugin tests and installation verification.
Keep rejected actual figures as project-local evidence; do not bundle private
manuscript images or source-paper artwork into the plugin.
