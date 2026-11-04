# Closed-Loop Scientific Figure Checklist

Use this checklist for paper or manuscript figures containing feedback, fallback, retry, update, or multiple interacting loops. It supplements the general academic playbook and the base edge-quality rules.

## Scientific Meaning Before Layout

1. Name each loop by its scientific function. Prefer names such as operation, cognition, learning, validation, or governance loop. Use `fast`/`slow` only when a cited source or a stated system timescale supports that distinction.
2. Write every non-primary connector as `source --relation--> target` before routing it. Confirm failure direction, update target, re-entry point, and loop closure separately.
3. Assign one stable meaning to each line style and state it in the legend or caption. A practical default is solid for the primary operational flow and dashed for fallback, retry, exception, or conditional return; do not use dashed lines merely as decoration.
4. Do not let proximity imply causality. A capability level, policy band, or contextual axis connects to a process node only when the manuscript establishes an explicit mapping, constraint, temporal, or causal relation.
5. Freeze the accepted content contract before a layout-only revision. Record stable node and edge IDs, exact visible labels, `source --relation--> target`, branch conditions, and line-style meanings. A spacing, routing, or port repair may change bounds, waypoints, connection points, and `labelOffset`; it must not silently rewrite the scientific content.
6. Record directed non-edges and forbidden inferences for independently terminating branches, monitoring-only outputs, and cross-domain paths that must not control the main loop. Record support or governance bands as cross-cutting regions with explicit presentation constraints.
7. Approve a low-detail wireframe at the target aspect ratio before detailed connector labels and typography. If a later repair moves the major process groups, reset the wireframe gate.

## Layout and Routing

1. Keep one dominant reading direction for the primary path. Route feedback and fallback paths through separate outer corridors so the main path remains traceable.
2. Do not let solid and dashed connectors share the same face slot, endpoint stub, or short corridor. Distribute connection points so each arrow can be followed from the node boundary at intended print scale.
3. Keep an orthogonal route orthogonal at its endpoints. With manual waypoints, align the first waypoint horizontally or vertically with the source attachment and the last waypoint with the target attachment; otherwise a diagonal first or last segment appears. Do not combine manual waypoints with explicit entry/exit hints when the base schema forbids that combination.
4. Keep return paths visibly clear of node borders. A U-shaped back-edge that hugs a box border can look like an extended border even when crossing counts are zero.
5. Avoid stacked or nearly coincident return paths. Separate corridors and arrowheads; color alone is not sufficient separation.
6. Remove redundant nodes that repeat semantics already present in a decision or action node. Extra constraint or status boxes are justified only when they introduce an independently referenced state, input, or boundary.
7. Establish the layout grid before routing. Align peer nodes to common row or column centerlines, keep equivalent nodes the same size, and use consistent gaps within a lane. Reserve separate corridors for the primary path, outer feedback, exception/fallback, and validation/retry paths before placing their connectors.
8. Assign ports by scientific role rather than by visual convenience. Keep primary-flow input/output on opposing faces when possible; use secondary top/bottom faces for feedback or re-entry; give exceptional and conditional paths distinct slots. The final segment must meet the target face orthogonally, and the arrowhead must read as terminating at that boundary rather than floating outside, entering a corner, or running along the border.
9. Prefer the simplest route that preserves semantic separation: straight for aligned primary edges and low-bend orthogonal routes for returns. A large detour used only to occupy whitespace weakens the hierarchy and is a layout defect.
10. Keep repeated container-title offsets, title-to-first-row clearance, peer-node gaps, and gaps between sibling lanes consistent. A support region must retain enough separation that it does not read as the next numbered process lane.

## Labels and Conditions

1. Omit an edge label when it only repeats the source or target node text.
2. Keep a branch condition on its edge when the relation would otherwise be ambiguous. Preserve frozen wording; move it with `labelOffset` and adjust wrapping or corridor spacing. Shorten only when content editing is authorized and the condition's meaning is preserved.
3. If no clean label corridor exists, place the condition in the decision outcome or destination node, or explain it in the legend/caption, but only when the arrow relation remains unambiguous.
4. Inspect for duplicated condition text, labels sitting on dashed segments, and labels that become detached from their branch after scaling.
5. Treat every edge label as owned by exactly one connector. Put a condition near the branch point or on a uniquely traceable straight segment, not midway between two boxes or loops where it can be mistaken for a node annotation or for a different edge.
6. Apply a label-ownership test at intended print scale: a reader should be able to point to the label's connector without first tracing multiple nearby lines. If not, move the label, move the route, or relocate the condition into a node/caption without changing its meaning.
7. Measure the label box, not only its anchor. Keep visible clearance from node borders, arrowheads, and unrelated connectors; text touching a frame or sitting tangent to a border is a blocking overlap even when the YAML anchor itself is outside the node.

## Typography and Monochrome Output

1. For Chinese manuscript figures that require 宋体 and Times New Roman, request a stack such as `Times New Roman,SimSun,<installed Songti fallback>`. The fallback is environment-specific.
2. Verify typography at three layers: the YAML/theme request, the generated `.drawio`/SVG `fontFamily`, and the fonts actually installed or embedded by the export environment. A `SimSun` name in the stack does not prove that SimSun rendered.
3. If SimSun is unavailable, retain it first for target-system resolution, use an installed Songti fallback for the local export, and disclose the fallback. Do not silently substitute Noto Serif CJK SC when the requirement is exact SimSun.
4. Distinguish grayscale from pure black-and-white. When the request is `strict-black-white`, visible fills and strokes use only black or white; gray is a defect rather than an acceptable hierarchy token. Use line weight, spacing, labels, and dash cadence to retain hierarchy.

## Final Evidence Gate

Deterministic validation is necessary but not sufficient. Zero node/edge crossings does not detect a border-hugging return path, a shared endpoint slot, a diagonal endpoint stub, weak dashes, font substitution, or a semantically redundant label.

Before completion:

1. Run strict structural validation.
2. Inspect the exported artifact at full size.
3. Inspect the same artifact at its intended A4, Word, PDF, or journal-column size, preferably inside the actual document build.
4. Trace each loop from source through every arrowhead to its re-entry point; check endpoint slots, outer corridors, border clearance, line-style meaning, and condition placement.
5. Confirm the requested font stack in the generated artifact and record any local fallback.
6. Recheck all previously reported visual defects after every rerender; a clean validator report never closes a visual issue by itself.
7. Compare the accepted-round semantic inventory after every layout revision: exact node and edge labels, source-target pairs, arrow directions, branch conditions, and line styles. Flag any unrequested difference as a regression.
8. Perform a label-ownership pass with the diagram reduced to its intended publication size. Confirm that each condition label remains closer and more clearly related to its own edge than to any adjacent box, arrow, or loop.
