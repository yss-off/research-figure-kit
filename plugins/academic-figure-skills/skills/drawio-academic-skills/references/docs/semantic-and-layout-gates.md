# Semantic and Layout Gates for Relation-Sensitive Figures

Use this reference for architecture, workflow, roadmap, or closed-loop figures where adjacency, containers, support bands, or cross-domain arrows could imply a relationship the source does not establish.

## Semantic Boundary Contract

Freeze more than the visible nodes and arrows. Record these fields in `semantic_inventory` before detailed geometry:

- `non_edges`: directed source-target pairs that must not appear as connectors;
- `forbidden_inferences`: interpretations the finished figure must not invite, plus the visual countermeasure;
- `cross_cutting_regions`: support, governance, deployment, evidence, or context regions that span process areas, with explicit presentation constraints.

Example:

```json
{
  "non_edges": [
    {
      "source": "monitoring",
      "target": "decision",
      "reason": "Monitoring evidence is stored for review and does not control the decision."
    }
  ],
  "forbidden_inferences": [
    {
      "id": "monitoring-controls-decision",
      "statement": "The monitoring output directly controls the decision stage.",
      "prevention": "Terminate monitoring independently and keep it outside the decision arrow corridor."
    }
  ],
  "cross_cutting_regions": [
    {
      "id": "engineering-support",
      "label": "Shared engineering support",
      "semantic_role": "non-sequential support",
      "member_node_ids": ["monitoring"],
      "presentation_constraints": [
        "Do not number the region as a process lane.",
        "Do not add a process arrow merely to show shared scope."
      ]
    }
  ]
}
```

The manifest validator detects unknown endpoints, duplicate boundary IDs, a declared non-edge that also exists as an edge, unknown cross-cutting members, and an unresolved wireframe gate. It cannot detect every visual implication; the exported-artifact review still owns that judgment.

## Wireframe Gate

Before typography, color, icons, or connector-label polishing, review a low-detail wireframe at the target aspect ratio. A text or monochrome shape wireframe is sufficient when it exposes:

- primary reading direction and process-lane order;
- loop closure and outer return corridors;
- independent termination points;
- cross-cutting regions and whether they are causal;
- prohibited cross-domain connections;
- approximate title bands, first-node rows, and bottom-note allocation.

Record `layout.wireframe_gate.status` as:

- `approved` when the structure was actually reviewed and no required user decision remains; the agent may review geometry within settled semantics unless the user explicitly required personal approval;
- `not_applicable` only for a genuinely simple, already-fixed edit, with a reason;
- `pending` while semantics or layout remain unresolved.

Strict or accepted manifest validation rejects a pending or absent gate. Approval freezes structure, not every pixel; later geometry edits may still improve spacing and routing without changing the semantic inventory.

In `decision`, identify who reviewed the structure (`agent` or `user`), the source or prior decision that settles semantics, and the review result; point `review_artifact` to the inspected wireframe where available. An agent review must never be described as user approval. Preserve existing user approval when its scope remains valid. Structural geometry changes require another review, not another user question unless they change scientific meaning or the user requested that checkpoint. Never mark unresolved semantics as approved to pass validation.

## Supplemental Academic Issue Types

The sibling base visual-review taxonomy remains authoritative for ordinary overlaps and routing defects. Academic relation-sensitive review may additionally record:

| Problem | Observable condition |
| --- | --- |
| `ambiguous-causality` | Adjacency, a continuous corridor, or unlabeled line makes an unsupported source-target influence plausible. |
| `false-process-lane` | A support, validation, deployment, evidence, or governance region looks numbered or sequenced like a primary process lane. |
| `inconsistent-spacing` | Peer lanes, nodes, titles, or region gaps that should repeat use visibly different spacing. |
| `title-border-crowding` | A lane or container title has insufficient visible clearance from the frame or first content row. |
| `font-render-mismatch` | Installed fallback changes the intended family, width, baseline, or line breaks enough to affect the figure. |
| `strict-monochrome-violation` | A figure explicitly requested as pure black and white contains gray or colored visible graphics. |

These are visual observations, not claims about hidden implementation. State the visible evidence and the smallest canonical change.

## Geometry Review at Target Size

Do not assign universal pixel thresholds. Instead, define repeated geometry tokens in the canonical layout and verify them at the intended document size:

1. title-to-top-frame clearance;
2. title-box-to-first-content-row clearance;
3. peer-node horizontal or vertical gaps;
4. gaps between sibling lanes or regions;
5. support-region and bottom-note separation;
6. outer feedback-corridor clearance from node and container borders.

Use deterministic measurements to detect inconsistencies, then inspect visible glyph ink in the exported artifact because font fallback can shift text inside nominally correct boxes.

## Color Policy

Distinguish:

- `grayscale`: black, white, and gray may be used;
- `black-white`: black and white are primary, but antialiasing or explicitly approved neutral treatment may remain;
- `strict-black-white`: visible fills and strokes must use only black or white; gray and color are defects.

When the user explicitly requests pure black and white, select `strict-black-white`. Do not reinterpret it as a grayscale palette. Record the source-level color scan and inspect the final raster/PDF because antialiasing is a renderer property, not a semantic palette change.

## Stopping Rule

Return to wireframe comparison instead of continuing local repairs when any of these occurs:

- a forbidden inference remains plausible after one targeted reroute;
- a cross-cutting region still reads as a process lane;
- more than two long cross-domain connectors compete for the same corridor; or
- typography and spacing repairs require moving the major process groups.

Once structure changes again, reset the wireframe gate and repeat the semantic inventory comparison before detailed rendering.
