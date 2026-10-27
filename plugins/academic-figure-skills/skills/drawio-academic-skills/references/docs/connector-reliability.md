# Reliable arrows in exported scientific diagrams

This guidance is for relation-sensitive workflow and architecture figures. It
complements the existing semantic and layout checks; it is not a universal
requirement to draw all scientific arrows orthogonally.

## What to control

1. Define what each arrow carries or asserts. A connector is a scientific
   relation; distinguish data, control, observation and feedback in context.
   Give line styles consistent meanings. Do not add junctions or merge paths
   merely to improve appearance.
2. Reserve the attachment face and the **straight landing corridor** before
   placing long return/cross-panel routes. For an orthogonal connector, enter
   its target perpendicular to the border. The last bend must leave room for
   the *exported* arrowhead, its stroke and a visible clearance, not just for
   the line endpoint. A roomy terminal segment is a local design choice, not
   a publisher-mandated numeric threshold.
3. Keep return corridors separate from panel borders and other routes. Use
   additional spacing, a better attachment face, or a simple routed polyline
   before adding more bends. If a layout cannot show its approved relations
   clearly, explain the tradeoff before changing a user-frozen layout.
4. Use native source/target-bound edges. Fixed anchors stabilize an attachment;
   floating anchors may move when a shape moves. Waypoints are **bends**, not
   arrow tips. Check the final rendered attachment after any move. Honor the
   bundled schema's rules for combining ports and waypoints; do not bypass
   them with raw XML patches.
5. Inspect the actual exported SVG/PNG: arrow tips, short end segments, borders,
   labels and incoming slots at intended print size. Zero crossings or a
   successful XML/schema/manifest check do not establish arrow readability.
   A clear SVG does not establish Desktop/Word rendering parity.

## Route planning before arrow styling

For a routing complaint, review the whole path rather than repairing only the
arrow tip. Keep user-approved grouping, scientific relations and line meanings.
The following is an authoring policy informed by graph-drawing research, not a
publisher-mandated style or a claim that an automatic router has been installed.

1. Write a short route ledger for affected edges: semantic source/target,
   attachment faces, intended corridor, obstacles, bends and exported length.
   Obstacles include node interiors, titles and annotations. A grouping frame
   may be crossed at a clear boundary; crossing it does not create a junction.
2. Reserve distinct channels for forward flow, return/feedback, and cross-panel
   results before fixing node coordinates. Prefer facing ports and direct paths
   or a short dogleg. First try modest spacing/alignment changes within the
   approved layout, rather than routing an adjacent relation around the page.
   For adjacent source and target layers, compare aligning their ports and
   using a vertical or horizontal straight connection before retaining a
   diagonal inherited from a reference. Preserve the actual source-target
   mapping, semantic grouping, readable spacing and arrow clearance; do
   not force alignment if it creates collisions or hides meaning. Oblique
   edges remain valid when they communicate geometry or better fit the
   approved layout; this is a design preference, not an IEEE rule.
3. Avoid unrelated objects, ambiguous junctions and coincident edge segments;
   then compare feasible routes for bends, length, border proximity and label
   association. These goals compete: do not minimize length at the expense of
   meaning or required separation. Longer paths may be justified by the actual
   topology. Record the reason instead of imposing a universal bend limit.
4. Place route labels adjacent to an identifiable segment in reserved whitespace.
   Prevent routes from cutting through titles or body text. Independently routed
   edges must not share a bus unless a bus/junction is scientifically intended.
   Line jumps may clarify unavoidable crossings when supported by the selected
   export backend; they do not fix gratuitous detours or stacked paths.
5. Remove redundant collinear waypoints and small avoidable doglegs in canonical
   YAML. Confirm actual exported ports, marker clearance and label avoidance.
   Compare before/after path geometry for affected edges and visually trace each
   route from source to target at the intended reading size. Preserve a layout
   tradeoff as `review` when evidence is insufficient; zero crossings and the
   arrowhead audit alone do not close a routing complaint.

## Acceptance check: direct input or justified detour

Optimize the complete composition before the bend count. Preserve readable
input spacing, label-to-object association, panel balance and author-approved
placement. A direct route is preferable only when its required alignment does
not worsen these properties or scientific meaning. Extra space and clear label
ownership are legitimate reasons to keep a short dogleg even in an empty
corridor. Do not move a tensor or stretch a panel merely to report more straight
lines. If a straighter variant is less readable or the author prefers the
previous balanced composition, retain that composition and record the tradeoff.

For a local input-to-module connector, compare a horizontal/vertical direct
route **after aligning its source and target ports** before accepting a dogleg.
A small coordinate mismatch alone is not a reason to keep two bends. When a
modest move is permitted, the direct corridor is clear and overall composition
is preserved or improved, align the input or
port, remove the waypoints in canonical YAML, and rerender. Check the whole
exported path and arrowhead again; do not shorten only its final segment.

For each affected bent connector in a routing review, record what the bends
avoid or communicate (an obstacle, a label, a distinct input slot, a residual
branch, a feedback corridor, input spacing, label association, or a frozen-layout constraint). If no purpose can
be identified, the routing complaint remains open even if the geometry and
arrowhead audits pass. This is a human layout acceptance check, not an automatic
bend detector or an IEEE/TWC requirement. Do not impose a numeric bend limit.
Retain useful residual and feedback paths; do not merge their semantics or
force straight lines through obstacles just to reduce bends.

Anonymous regression example: an input rectangle has a top exit at x=120;
its consumer has a bottom entry at x=100, with no intervening object. The route
(120,300) -> (120,250) -> (100,250) -> (100,200) is connected correctly but has
an avoidable alignment detour. If moving the input is within scope, align its
exit to x=100 and draw one upward arrow. Counterexample: a label or another
module occupies that direct corridor, or a fixed port carries a distinct role;
then preserve a clear routed connection and document why. These are local
illustrative coordinates, not publisher thresholds.

The existing `audit_connectors.py` checks arrowhead landing space and optional
orthogonality only. It does **not** implement this route planner, detect all
obstacles, measure route optimality or certify readability. Do not report its
PASS as a routing audit PASS.

Research and implementation references:

- Wybrow, Marriott and Stuckey, *Orthogonal Connector Routing*, GD 2009,
  https://users.monash.edu/~mwybrow/papers/wybrow-gd-2009.pdf . Author-hosted
  indexed abstract/conclusion describe object avoidance and a monotonic cost
  of path length and bends. Full PDF access can be restricted. Crossing costs
  were future work there; do not attribute a zero-crossing guarantee to it.
- Marriott, Stuckey and Wybrow, *Seeing Around Corners: Fast Orthogonal Connector
  Routing*, 2014, https://users.monash.edu/~mwybrow/papers/marriott-diagrams-2014.pdf .
  Author-hosted indexed abstract/introduction describe visibility-graph routing,
  bend/length optimization and ordering/nudging connector paths.
- draw.io native auto-routing and waypoint controls:
  https://www.drawio.com/docs/manual/connectors/connectors-auto-route/ and
  https://www.drawio.com/docs/manual/connectors/waypoints-connectors/ .
  Native editor documentation does not establish standalone export parity.
- Graphviz `splines`: https://www.graphviz.org/docs/attrs/splines/ explicitly
  notes limitations of orthogonal routing with ports/edge labels. Automatic
  orthogonal style selection is not sufficient evidence of good routing.

## Focused SVG preflight

For the bundled standalone SVG export, run:

```bash
python scripts/audit_connectors.py figure.svg --orthogonal --strict \
  --output /tmp/figure-connectors.json
```

Omit `--orthogonal` for intentionally oblique arrows. This read-only helper
compares the final straight run with the SVG marker viewport's backward extent.
SVG's default `markerUnits="strokeWidth"` means a larger line width also enlarges
the head. For a markerWidth of 8 and stroke-width of 2.25, the viewport extent is
18 SVG user units; an 8-unit final segment is too short to contain it.

`arrowhead_over_bend` is a conservative geometry warning, not a scientific or
publication verdict. The estimate excludes marker stroke caps and filters;
passing it does not prove attachment or collision clearance. Curves, transforms,
CSS sizing and unsupported marker geometry are reported as `not_audited` and
require the appropriate renderer/manual review, rather than receiving a PASS.
The CLI returns nonzero for unaudited geometry; `--strict` also fails warnings.

Repair **canonical YAML geometry**, rerender and rerun the preflight. Do not
postprocess the SVG path, marker or PNG to hide a source defect. Record the
before/after finding and visually check the final arrow again.

## Renderer boundary

The pinned base standalone SVG backend is an approximation of draw.io. In the
currently bundled base, marker definitions are fixed and `renderEdge` does not
read `endSize`/`startSize`. Merely changing `endSize` in XML may therefore leave
SVG arrowheads unchanged. Verify the selected backend's output; do not assume
native Draw.io and standalone SVG interpret style fields identically.

If a defect belongs to that base, retain a minimal reproduction and its upstream
commit in the engineering issue record. Update the base through its approved
upstream process; this overlay audits and guides authoring, not a private fork of
the base renderer. Do not edit installed plugin caches during ordinary drawing.

## Sources and evidence boundaries

- Bang Wong, *Arrows*, Nature Methods 8, 701 (2011),
  https://www.nature.com/articles/nmeth.1676 . The publicly accessible introduction
  explains that arrow meaning depends on context; the subscription-only body
  was not used to infer numeric routing rules.
- Rougier, Droettboom and Bourne, *Ten Simple Rules for Better Figures*, PLOS
  Computational Biology (2014),
  https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1003833 .
  Supports audience-, medium- and clarity-based review, not a universal arrow style.
- draw.io, fixed vs floating connectors:
  https://www.drawio.com/docs/manual/connectors/connector-fixed-vs-floating/ .
- draw.io, waypoints:
  https://www.drawio.com/docs/manual/connectors/waypoints-connectors/ .
  Its native editor behavior is not proof of standalone-backend behavior.
- draw.io, automatic routing:
  https://www.drawio.com/docs/manual/connectors/connectors-auto-route/ .
- The measured 8-unit run and 18-unit marker footprint come from a locally
  exported diagram and bundled base source inspection, not from a publication
  requirement. No client figure content is needed by the regression fixtures.
