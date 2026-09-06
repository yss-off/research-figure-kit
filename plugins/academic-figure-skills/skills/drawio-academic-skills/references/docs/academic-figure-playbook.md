# Academic Figure Playbook

Use this playbook whenever `meta.profile = academic-paper` or the user asks for a paper, thesis, journal, IEEE, manuscript, or research figure.

## Step 1: Classify the Figure

Before drafting nodes, answer one question:

What is this figure mainly explaining?

- **Structure** -> `meta.figureType: architecture`
- **Progression** -> `meta.figureType: roadmap`
- **Execution** -> `meta.figureType: workflow`

If the answer is mixed, pick the dominant purpose. If the diagram tries to explain structure, progression, and branching control logic at the same time, split it into two figures.

## Figure Types

### Architecture

Use for:

- system composition
- module boundaries
- data movement between tiers
- runtime responsibilities
- model architectures such as CNN, YOLO, Transformer, encoder-decoder, feature fusion, or multi-head prediction

Quality cues:

- group subsystems clearly
- emphasize layers or boundaries
- avoid turning the diagram into a chronological pipeline
- use modules for stages and semantic node types for layers, tensors, operators, and outputs
- keep layer labels compact; move tensor sizes, assumptions, or metrics into callouts or legends when needed

### Roadmap

Use for:

- study phases
- milestone progression
- delivery stages
- stage outputs

Quality cues:

- make progression directional
- show only major stages
- surface the output or decision at the end of each stage

### Workflow

Use for:

- ordered steps
- decisions and branching
- loops and fallback paths
- procedural execution
- method pipelines, ablation studies, experiment procedures, and validation loops

Quality cues:

- keep the step order obvious
- label ambiguous decisions
- keep back-edges and loops sparse and readable

## Scientific Figure Patterns

Worked examples under `references/examples/` (render via the sibling base CLI):

- `yolo-model-architecture-paper.yaml` — model-architecture pattern (YOLO backbone/neck/head).
- `max-pooling-operation-paper.yaml` — operation/mechanism pattern (max-pooling grid with explicit bounds).
- `ablation-study-pipeline.yaml` — experiment-pipeline pattern (ablation variants over shared evaluation).
- `research-pipeline.yaml` — experiment-pipeline pattern (end-to-end research workflow).
- `system-architecture-paper.yaml` — architecture figure type (paper system overview).
- `industrial-architecture-cn-paper.yaml` — architecture figure type (Chinese-thesis industrial system).
- `ieee-network-paper.yaml` — architecture figure type with network stencils (IEEE style).
- `technical-roadmap-paper.yaml` — roadmap figure type (milestone phases).

### Model Architecture

Use this pattern for CNN, YOLO, Transformer, encoder-decoder, and feature-fusion figures.

- Set `meta.figureType: architecture`.
- Use 3-5 modules for major stages such as Input, Backbone, Fusion/Neck, Prediction Head, Loss, or Output.
- Prefer semantic types: `input`, `tensor3d`, `conv`, `pool`, `attention`, `feature`, `operator`, `loss`, and `output`.
- Keep tensors and operators visually small. Use a legend for repeated layer notation instead of repeating long descriptions in every box.
- Show only the architectural relationships needed for the paper argument; detailed implementation hyperparameters belong in the caption or body text.

### Operation Or Mechanism

Use this pattern for max pooling, attention scoring, gating, residual add, normalization, or algorithm-step illustrations.

- Pick `workflow` when the figure explains an ordered operation, and `architecture` when it explains a static mechanism inside a model.
- Use explicit `bounds` for small grids, matrices, formula boxes, callouts, and operator nodes.
- Use native rectangles/text cells for grids or matrices. Do not use a screenshot of the operation as the final draw.io page.
- Keep formulas short and use supported math delimiters from `math-typesetting.md`.
- Offset arrows and edge labels with `labelOffset` so labels do not sit on connector lines.

### Experiment Pipeline

Use this pattern for datasets, treatments, ablations, simulations, or evaluation workflows.

- Set `meta.figureType: workflow`.
- Separate setup/data, variants or methods, shared evaluation, metrics, and reporting.
- Draw ablation branches in parallel and converge them before validation or metrics.
- Label branches with short method names. Use the legend for line styles, color encodings, or metric abbreviations.

### Orthogonal Process and Capability Axes

Use this pattern when one figure must show both an operational loop or pipeline and a separate capability, maturity, abstraction, or time progression.

- Declare one axis as the primary reading path and the other as contextual progression; keep their labels, arrow styles, and whitespace visually distinct.
- Keep process arrows inside the operational path. Use a band, bracket, ladder, or axis marker for progression instead of reusing process connectors.
- Do not draw arrows from a maturity/capability level to a process step merely because they are adjacent. Add a cross-axis arrow only when the source supports a causal, temporal, or explicit mapping relation, and label that relation.
- If cross-axis mappings become dense, split the process and progression into separate figures or panels rather than shrinking labels or adding crossing arrows.
- Audit the closed loop from observation/input through action/output and back to feedback/update; audit the progression independently from lower to higher capability.

### Reference-Image Redraw

Use this pattern when a paper screenshot or existing figure must become editable.

- Use `meta.source: replicated`.
- Preserve captions, legends, formulas, callouts, section headers, and connector labels as first-class elements.
- Use `meta.canvas: WIDTHxHEIGHT` and top-left `bounds` when matching the source coordinate system matters.
- Rebuild the main diagram with native draw.io cells and verify the exported SVG or Desktop artifact before any browser screenshot.

## Visual Defaults

- prefer white or very light backgrounds
- use low-saturation colors unless the user explicitly wants a color paper figure
- keep one dominant reading direction
- align nodes to the grid instead of hand-placing them loosely
- preserve frozen labels; adjust wrapping, bounds, and spacing before shrinking fonts; shorten wording only when content editing is authorized and meaning is preserved
- use consistent line weights, arrowheads, and corner radii
- make every arrow express a short `source --relation--> target` statement; distinguish process, feedback, control/fallback, and progression by line style and legend, not color alone
- keep text, callouts, captions, and legends transparent (`fillColor=none`, `labelBackgroundColor=none`) and sized just wider than their content, not stretched to a container — see `../drawio/references/docs/design-system/tokens.md` § Text & Label Styling

## Terminology and Abbreviations

- Treat the figure as a standalone scholarly object. Expand every Latin-letter abbreviation at its first figure-visible use; do not rely only on a surrounding paragraph that may be separated from the figure during review or reuse.
- When a bilingual full form would overcrowd a node, keep the node label concise and define the abbreviation earlier in a figure-internal legend or caption. A suitable pattern is `中文全称（English full name, ABBR）`, adapted to the venue language.
- Do not invent uncommon abbreviations merely to make boxes fit. Shorten prose, move detail to a legend/caption, or split the figure before compressing terminology into unexplained initials.
- Use the same term and abbreviation consistently across nodes, edge labels, legend, caption, and manuscript text.

## Venue Palette Mapping

After determining the venue, choose `meta.palette` independently from the theme. Apply an explicit palette or unambiguous style directly; otherwise use the venue recommendation when it satisfies the requested print and accessibility constraints. Ask only when the user requests selection or a material tradeoff remains unresolved. Use the current environment's available question mechanism and option limits, or a concise conversational question. Explain the palette's display name, venue fit, and colorblind/grayscale safety; do not require a legacy tool or repeat an already resolved choice.

| Venue or scenario             | Recommended  | Alternatives                                              |
| ----------------------------- | ------------ | --------------------------------------------------------- |
| IEEE print / camera-ready     | `ieee-bw`    | `tol-high-contrast`, `ieee-color`                         |
| IEEE online / conference      | `ieee-color` | `matlab-lines`, `okabe-ito`                               |
| Elsevier / general journal    | `okabe-ito`  | `tol-bright`, `tol-muted`, `seaborn-colorblind`           |
| Nature / Science family       | `okabe-ito`  | `tol-muted`, `journal-npg` (aesthetic only; not CVD-safe) |
| Chinese thesis (`cn-thesis`)  | `ieee-bw`    | `tol-high-contrast`, `journal-jama`                       |
| Engineering architecture / C4 | `c4-blue`    | `cloud-aws`, `drawio-classic`                             |
| Cloud architecture            | `cloud-aws`  | `c4-blue`                                                 |

For replication, preserve the source palette and skip this question unless the user explicitly asks to normalize or recolor the figure.

## Academic Delivery Matrix

Use this table as the single authority for primary output selection. Always deliver editable `.drawio`; then select exactly one primary delivery class:

| Delivery class        | Use when                                                        | Required primary artifact                                      | Honest fallback or stop condition                                                                 |
| --------------------- | --------------------------------------------------------------- | -------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| `raster-publication`  | Word, thesis, Pandoc/LaTeX raster-first, A4, or explicit raster | 300ppi-effective PNG                                           | Prefer Desktop; otherwise use the source-preserving browser-rasterized derivative gate            |
| `vector-submission`   | Journal/venue requires vector                                   | PDF or SVG with text converted to paths                        | IEEE accepts PS/EPS/PDF, not SVG; if no accepted exporter exists, report publication export blocked |
| `draft-preview`       | Review/draft or publication target is not fixed                 | Live-text SVG labeled preview/intermediate                     | Do not claim publication completion; resolve the target before final delivery                      |

Keep reproducibility records in the work directory: `.spec.yaml`, `.arch.json`, and the figure manifest. Record the selected value in `manifest.contract.delivery_class`.

Honor additional user-requested formats, but keep one primary class. A requested live-text SVG may accompany a paper task as a preview; it does not satisfy raster or vector publication delivery. If the target is ambiguous, use `draft-preview` and report the unresolved publication artifact instead of guessing.

## Node Budget Management

Academic figures should be clear and focused. Keep node count under 40 for optimal readability.

### Budget Guidelines

**Recommended targets by figure type** (layout heuristics, not scientific or venue standards; exceeding a target calls for readability review, not automatic confirmation or content deletion):

| Figure Type  | Target Nodes | Maximum Nodes | Typical Distribution                     |
| ------------ | ------------ | ------------- | ---------------------------------------- |
| Architecture | 30-35        | 60            | 4-6 modules × 5-7 nodes + legend (1-2)   |
| Workflow     | 25-30        | 50            | 15-20 steps + 5-8 decisions + legend (1) |
| Roadmap      | 15-20        | 40            | 10-15 stages + 3-5 outputs + legend (1)  |

**System warnings**:

- 0-40 nodes: no warning (ideal range)
- 41-60 nodes: warning (conversion succeeds, but consider simplification)
- 61-100 nodes: error (blocked in strict mode, split strongly recommended)
- > 100 nodes: fatal (always blocked, hard limit)

### Node-Efficient Patterns

Ready-made compact templates live under `references/templates/`: `multi-module-system-compact.yaml` (multi-module system inside the recommended budget) and `neural-network-architecture-compact.yaml` (neural-network architecture inside the recommended budget). Start from these before authoring node-heavy figures from scratch.

#### Example 1: Legend

**❌ Expanded Legend (wastes 12 nodes)**:

```yaml
- id: legend_container
  label: "Legend"
  bounds: { x: 1000, y: 400, width: 200, height: 160 }
  style: { fillColor: "#FAFAFA" }

- id: legend_arrow_solid
  label: ""
  bounds: { x: 1010, y: 430, width: 40, height: 2 }
  style: { strokeColor: "#1E3A5F", strokeWidth: 2 }

- id: legend_arrow_label
  type: text
  label: "Data flow"
  bounds: { x: 1060, y: 426, width: 120, height: 16 }
  style: { fontSize: 11 }
# ... 10 more nodes for each legend item
```

**✅ Compact Legend (1 node)**:

```yaml
- id: legend
  type: text
  label: |
    Legend

    → Data flow
    ⇢ Conditional flow
    ⊙ Hadamard product
    ∥ Concatenation

    ■ Zone A: Feature extraction
    ■ Zone B: Conditional embedding
  style:
    align: left
  # no bounds/fontSize: the converter sizes the box and applies the 16px text ladder
```

**Savings**: 12 nodes → 1 node (11 nodes saved)

#### Example 2: Decorative Elements

**❌ Detailed Bar Chart (wastes 8 nodes)**:

```yaml
- id: bar_1
  label: ""
  bounds: { x: 100, y: 512, width: 18, height: 36 }
  style: { fillColor: "#22C55E" }

- id: bar_2
  label: ""
  bounds: { x: 122, y: 524, width: 18, height: 24 }
  style: { fillColor: "#4ADE80" }
# ... 6 more bars
```

**✅ Simplified Representation (1 node)**:

```yaml
- id: attention_weights
  label: "ωₜ weight bars (t=1..L)"
  bounds: { x: 100, y: 512, width: 320, height: 48 }
  style:
    fillColor: "#E8F5E9"
    strokeColor: "#16A34A"
```

**Savings**: 8 nodes → 1 node (7 nodes saved)

### When to Split

Split into multiple figures when:

- Node count approaches 50 and simplification is not practical
- The diagram explains 3+ distinct mechanisms or stages
- Readers would need to zoom in to read labels at normal page size
- The figure serves multiple purposes (e.g., architecture + training procedure)

### Split Strategies

**By data path** (for multi-input or multi-branch systems):

- Figure 3a: High-frequency processing path
- Figure 3b: Low-frequency conditioning path
- Both figures share the same fusion/output stage context in captions

**By hierarchy level** (for deep architectures):

- Figure 3a: System overview (4-6 major modules)
- Figure 3b: Detailed view of the fusion module
- Figure 3c: Attention mechanism internals

**By mechanism** (for multi-stage methods):

- Figure 3a: Feature extraction stage
- Figure 3b: Conditional fusion mechanism
- Figure 3c: Temporal attention and regression

**Real-world example from IEEE papers**:

- Typical neural network figures: 25-35 nodes
- Complex architectures often split into 2-3 sub-figures
- Main figure shows 4-6 modules; detail figures zoom into 1-2 modules

## Canvas and Print Sizing

A figure is scaled to the column width of the paper, so canvas pixels have no fixed print size. When a figure is placed at full column width:

```
effective pt = fontSize x print-width-pt / canvas-width-px
```

Print targets (set `meta.print` to opt in):

| `meta.print.target` | Width          | Label floor |
| ------------------- | -------------- | ----------- |
| `cn-thesis`         | 155mm = 440pt  | 9pt (小五)  |
| `ieee-single`       | 3.5in = 252pt  | 8pt         |
| `ieee-double`       | 7.16in = 516pt | 8pt         |

`meta.print: { target: cn-thesis }` (or custom `widthPt` / `minPt`) makes the validator check every figure. Without `meta.print`, only canvases wider than 1500px are checked, against the IEEE single-column floor.

**Minimum label fontSize for the floor to hold**:

| Canvas width | cn-thesis (440pt/9pt) | Single column (252pt/8pt) | Double column (516pt/8pt) |
| ------------ | --------------------- | ------------------------- | ------------------------- |
| 630px        | 13                    | 20                        | 10                        |
| 800px        | 17                    | 26                        | 13                        |
| 1000px       | 21                    | 32                        | 16                        |
| 1200px       | 25                    | 39                        | 19                        |
| 1600px       | 33                    | 51                        | 25                        |

Practical prescriptions:

- Let the font ladder work: without explicit `style.fontSize`, labels get module 22 / node 20 / edge 18 / text 16 and boxes grow to fit, so layout density — not font size — decides the canvas width.
- Pick `meta.print` from the venue first, then keep the canvas narrow enough for the table above; split the figure before shrinking fonts.
- Wide architecture figures are double-column or full-text-width material; do not squeeze them into a single column.
- IEEE vector submissions accept PS/EPS/PDF only (SVG is not on the list). Export a PDF via draw.io Desktop for IEEE targets.

## Final Quality Gate

Do not consider the figure complete until all of these are true:

- `meta.figureType` is set correctly
- the diagram reads clearly at normal A4 page zoom
- colors are not the only carrier of meaning
- the selected palette matches the venue mapping and its colorblind/grayscale flags are reported
- grayscale-unsafe print selections are replaced with `ieee-bw` or `tol-high-contrast`, or the strict validation failure remains explicit
- labels are concise and readable
- Latin-letter abbreviations are expanded at first figure-visible use or defined earlier in the figure legend/caption
- every arrow has an auditable source, relation, and target; arrow direction and loop closure match the confirmed scientific meaning
- connector routing is clean enough that the reading order is obvious
- `.drawio`, sidecars, manifest, and the selected class's primary artifact are aligned
- `raster-publication` has a 300ppi-effective PNG; `vector-submission` has an accepted PDF/path-only SVG; `draft-preview` has SVG and is not described as publication-final
- visual self-check uses the class's exported primary artifact; a derivative-gate browser-rasterized PNG counts as an artifact, while an ad hoc browser/live screenshot does not
- every additional requested companion matches the final diagram state
