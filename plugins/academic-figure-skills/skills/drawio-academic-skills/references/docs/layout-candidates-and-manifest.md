# Layout candidates, reference index, and figure manifest

Use this reference for complex, ambiguous, paper-derived, multi-loop, or reference-redraw tasks. It adds planning and evidence records around the existing sibling-base YAML/render workflow; it does not replace that workflow.

## Contents

- [When to compare candidates](#when-to-compare-candidates)
- [Candidate contract](#candidate-contract)
- [Reference-index contract](#reference-index-contract)
- [Selection gate](#selection-gate)
- [Figure-manifest contract](#figure-manifest-contract)
- [Artifact and QA evidence](#artifact-and-qa-evidence)
- [End-to-end commands](#end-to-end-commands)
- [Stopping rules](#stopping-rules)

## When to compare candidates

When no suitable layout is already fixed, generate 2–3 layout plans before authoring final YAML when any condition holds:

- the source is a paper, long technical description, or ambiguous reference image;
- the figure mixes a primary process with capability, maturity, time, or evidence axes;
- feedback, fallback, retry, or multiple loops need separate corridors;
- several sections could be expressed as layers, lanes, branches, or hero/support regions;
- the node budget or intended print width makes a split plausible; or
- the user explicitly asks to compare layouts.

Reuse an already-fixed plan, and skip candidate comparison for cosmetic edits, regardless of node count. Record why comparison was unnecessary. Do not turn a cosmetic edit into a redesign exercise.

Candidates are structured plans, not three polished figures. They must not change node labels, scientific relations, formulas, abbreviations, or evidence merely to look different.

## Candidate contract

Run the deterministic planner after extracting the confirmed major sections:

```bash
python scripts/layout_candidates.py \
  --figure-type workflow \
  --major-section "Data collection" \
  --major-section "Preprocessing" \
  --major-section "Modeling" \
  --major-section "Validation" \
  --has-feedback
```

Every candidate records:

- stable candidate ID and layout family;
- primary reading axis;
- section order and placement intent;
- edge/corridor strategy;
- strengths, risks, and use-when condition;
- the current playbook node-budget target; and
- `scientific_content_status: unchanged`.

The helper uses only the figure type and confirmed section/axis flags. It does not infer edge direction, causality, formulas, branch conditions, or the paper's contribution.

## Reference-index contract

Query bundled examples before inventing a layout from scratch:

```bash
python scripts/reference_index.py \
  --figure-type architecture \
  --feature deep-learning \
  --limit 3
```

`references/reference-index.json` contains only overlay-bundled examples and templates covered by the overlay MIT license. Each entry has a stable ID, path, figure type, layout features, use/avoid guidance, source, and license.

Use the index as a retrieval layer, not a gallery to copy blindly:

- adopt abstract layout features such as layering, branch convergence, compact legends, or stage compression;
- keep the current task's semantic inventory and exact text;
- do not copy external data, labels, trademarks, icons, or protected compositions;
- record selected and rejected reference IDs in the figure manifest; and
- add an external reference only after fixing its source/version and reviewing its license.

## Selection gate

Present candidates compactly. For each, state:

```text
candidate ID — main reading axis
best when: ...
main risk: ...
reference prior: ...
```

Select one candidate using the settled scientific argument, intended width, node budget, loop structure, and text density; record its ID and reason. The agent may select routine geometry. Wait only if the user explicitly requested plan approval or a material scientific decision remains unresolved; ask for that relation rather than a cosmetic preference. Reuse prior selections whose scope is unchanged.

Once selected, freeze the semantic inventory before geometry work:

- stable node IDs, exact labels, and roles;
- stable edge IDs and `source --relation--> target`;
- branch conditions and line-style meanings;
- formulas and abbreviation definitions; and
- panel/section membership.

For relation-sensitive figures, also freeze directed `non_edges`, `forbidden_inferences`, and `cross_cutting_regions`. Then review a low-detail wireframe at the target aspect ratio and record `layout.wireframe_gate` as `approved`, `pending`, or `not_applicable` with a reason. A structural redesign resets this gate. See `semantic-and-layout-gates.md`.

A later layout-only repair may change bounds, waypoints, ports, and label offsets. It must not silently change this inventory.

## Figure-manifest contract

Initialize an overlay-local manifest:

```bash
python scripts/figure_manifest.py init \
  --figure-id figure-3 \
  --title "Proposed system architecture" \
  --figure-type architecture \
  --output .drawio-tmp/figure-3/figure.manifest.json
```

The manifest schema is `assets/schemas/figure-manifest.schema.json`. Its top-level fields are:

- `contract`: venue, figure type, primary delivery class, communication goal, intended claim, language, palette, and print target;
- `semantic_inventory`: nodes, edges, abbreviations, formulas, non-edges, forbidden inferences, and cross-cutting regions;
- `layout`: compared candidates, selected ID, selection reason, and wireframe gate;
- `reference_selection`: index version, selected/rejected IDs, and adopted abstract features;
- `render`: canonical YAML path, artifacts, and exact base CLI commands;
- `qa`: deterministic, visual, and publication checks plus residual risks; and
- `provenance`: source records, transformations, and tool versions.

Use `pending` or `not_checked` for missing evidence. Never fill a PASS because a field is inconvenient to verify.

## Artifact and QA evidence

Each artifact record contains:

```json
{
  "role": "svg",
  "path": "outputs/figure-3.svg",
  "evidence_label": "command-executed",
  "renderer": "sibling-base standalone SVG"
}
```

Allowed evidence labels follow the sibling visual-review contract: `recorded-fixture`, `command-executed`, `Desktop-executed`, `browser-rasterized`, `model-executed`, and `missing-evidence`.

`build` validates the manifest, reads every present artifact, and records SHA-256 and size without changing diagram files:

```bash
python scripts/figure_manifest.py build \
  .drawio-tmp/figure-3/figure.manifest.draft.json \
  --output .drawio-tmp/figure-3/figure.manifest.json \
  --strict
```

QA layers remain separate:

- `deterministic`: sibling CLI/schema/strict-warning evidence;
- `visual`: exported-artifact inspection, round, and structured issues;
- `publication`: print size, caption/legend, formulas, abbreviations, palette/font, and venue-specific manual checks.

The manifest validator checks record structure and hashes. It also rejects unknown non-edge endpoints, a declared non-edge that is present as an edge, duplicate forbidden-inference IDs, unknown cross-cutting members, and a pending wireframe gate in strict/final validation. It cannot prove that every forbidden inference has been visually eliminated, or validate scientific meaning, copyright safety, visual quality, or current venue rules.

Set exactly one primary `contract.delivery_class`: `raster-publication`, `vector-submission`, or `draft-preview`. Strict validation requires PNG for raster publication, PDF or `text_mode: paths` SVG for vector submission, and SVG for draft preview. `.drawio` remains mandatory in every class; secondary requested formats may be recorded alongside the primary artifact.

## End-to-end commands

```bash
# 1. Compare plans and query local priors.
python scripts/layout_candidates.py --figure-type architecture \
  --major-section Input --major-section Backbone \
  --major-section Fusion --major-section Output
python scripts/reference_index.py --figure-type architecture --feature deep-learning

# 2. Author canonical YAML and render with the sibling base.
node ../drawio/scripts/cli.js figure.yaml figure.drawio \
  --validate --write-sidecars --sidecar-dir .drawio-tmp/figure --strict-warnings
node ../drawio/scripts/cli.js figure.yaml figure.png --validate --use-desktop

# 3. Record artifacts and validate the complete evidence bundle.
python scripts/figure_manifest.py build \
  .drawio-tmp/figure/figure.manifest.draft.json \
  --output .drawio-tmp/figure/figure.manifest.json --strict
```

If Desktop is unavailable, apply `academic-figure-playbook.md § Academic Delivery Matrix`: raster publication may use the source-preserving browser derivative gate in `academic-export-checklist.md`; vector submission needs a permitted exporter for the accepted format; draft preview needs SVG. Record the actual renderer. Mark only artifacts that cannot be produced through a permitted path as `missing-evidence`, and deliver the available editable source and preview without claiming publication completion.

## Stopping rules

- Compare at most three plans; more options usually duplicate layout families without adding evidence.
- Select one plan before detailed YAML geometry. Do not fully render every candidate unless the user explicitly requests that cost.
- Follow the sibling visual-review progress check: reassess after two repair rounds, continue authorized reversible repairs with a concrete improvement path, and finish when required checks pass. A round count alone is not a reason to leave a fix unfinished.
- Stop only the affected work when repeated attempts make no progress, a scientific decision remains unresolved, a content change or external transfer lacks authorization, no permitted export path can produce a required artifact, or a base-runtime change is needed. Continue independent work and report the specific missing decision or evidence.
- If the defect belongs to the sibling base, record it as a base issue; do not vendor a private runtime patch into this overlay.
