# Academic Publication Overlay

This file contains overlay-only policy for `drawio-academic-skills`. Shared schemas, CLI commands, design-system references, official XML/style mirrors, examples, themes, and workflow guides live in the sibling base skill at `../drawio`.

## Overlay Responsibility

Use this overlay when the request is publication-facing:

- paper, thesis, journal, IEEE, manuscript, camera-ready, or publication-ready figure
- A4 or Word/LaTeX export expectations
- academic formula figure or paper diagram replication
- research workflow, system architecture paper figure, or scholarly roadmap

## Required Academic Decisions

Before rendering, decide:

1. Venue or audience.
2. `meta.figureType`: `architecture`, `roadmap`, or `workflow`.
3. Palette selection and safety policy: venue recommendation, colorblind safety, and grayscale/print safety.
4. Caption and legend requirements.
5. Formula/text placement fidelity.
6. Primary delivery class from the playbook matrix, requested companion exports, and whether draw.io Desktop or another path-capable exporter is required.

## Palette and Print Policy

Use the single venue mapping in `academic-figure-playbook.md § Venue Palette Mapping`; do not maintain a second recommendation table here. Theme and palette remain independent: theme owns academic typography/layout treatment, while `meta.palette` supplies category colors.

When `meta.print.target` is `cn-thesis`, `ieee-single`, or `ieee-double`, a selected palette with `grayscaleSafe: false` emits `PALETTE_PRINT_GATE`. Normal validation reports a warning; strict validation escalates it to an error and recommends `ieee-bw` or `tol-high-contrast`. A non-colorblind-safe academic palette emits `PALETTE_CVD_NOTICE` as info so an intentional aesthetic choice remains possible.

Completion reports name the selected palette, its colorblind/grayscale safety flags, and any print-gate downgrade.

## Source Understanding

Use the source mode before drafting YAML:

- Document or paper: extract the research problem, gap, objective, theory or assumptions, data, method, mechanism, validation, metrics, findings, and contribution.
- Reference image: extract visible containers, swimlanes, section labels, nodes, arrows, captions, legends, formulas, colors, line styles, and ambiguous text.
- Text-only request: infer a compact academic figure plan and keep assumptions explicit.

For paper-derived figures, classify the source first:

| Source type                     | Figure pattern                                                                                |
| ------------------------------- | --------------------------------------------------------------------------------------------- |
| Algorithm or optimization paper | inputs -> assumptions -> model stages -> execution -> feedback -> scenarios -> metrics        |
| Empirical study                 | question -> hypotheses/constructs -> data/sample -> variables -> method -> checks -> findings |
| Mechanism study                 | antecedents -> mediators -> moderators/boundaries -> outcomes -> evidence                     |
| System architecture paper       | data/sensing -> processing modules -> decision/control -> outputs -> evaluation               |
| Experimental study              | problem -> setup -> treatment/control -> measurement -> analysis -> findings                  |
| Review or policy paper          | problem space -> classification -> evidence groups -> synthesis -> gaps/recommendations       |
| Deep-learning model paper       | input -> backbone/encoder -> fusion/attention -> head/decoder -> loss/output -> metrics       |
| Algorithm mechanism figure      | local inputs -> operation window -> formula/operator -> output -> interpretation              |

Map the result to the existing `meta.figureType` contract:

- `architecture`: structure, layers, modules, systems, actors, or static relationships.
- `roadmap`: study stages, milestones, phases, or progressive deliverables.
- `workflow`: ordered execution, branching, iterative methods, experiments, or pipelines.

## Scientific Figure Planning

When the source is a research model, mechanism, or experiment, turn the evidence chain into a compact figure plan before drafting YAML. The figure-type pattern library (model architecture, operation/mechanism, experiment pipeline, scholarly framework redraw — each with its YAML emphasis) lives in `academic-figure-playbook.md § Scientific Figure Patterns`; use it rather than re-deriving patterns here.

For complex tasks without an already-fixed layout, use `layout-candidates-and-manifest.md`: query the local reference index, compare 2–3 structurally distinct plans, record one selection, and freeze the semantic inventory. Reuse settled plans for cosmetic edits. Plans may change layout family and routing intent, but must keep labels, relations, formulas, abbreviations, and evidence unchanged.

Prefer an architecture figure for static relationships and a workflow figure for ordered operations. Do not invent a new `meta.figureType` when the existing three values can express the paper role.

## Research Evidence Chain

Extract a compact evidence chain before proposing the figure:

1. Research problem and gap.
2. Objective or research question.
3. Inputs, data sources, sample, variables, or operating conditions.
4. Theory, assumptions, hypotheses, constructs, or constraints.
5. Core method, model, algorithm, mechanism, or framework.
6. Actors, system components, scenarios, or process stages.
7. Outputs, experiments, validation methods, metrics, and results.
8. Main contribution, implications, limitations, or future-work hook.
9. Feedback loops, uncertainty, or boundary conditions when they affect interpretation.

Do not force every item into the figure. Include the items that explain the paper's argument and distinguish the proposed approach.

## Diagram Plan Gate

For complex figures without a fixed plan, record the plan before rendering. Select routine geometry autonomously when semantics and scope are settled. Ask only for an unresolved scientific relation, an unapproved content change, or a plan approval explicitly requested by the user; do not repeat an existing approval. Use this template:

```text
Source type:
Figure type:
Primary research chain:
Major sections:
Supporting nodes:
Key arrows and feedback:
Formula/callout placement:
Validation and contribution:
Preview path:
Terms needing confirmation:
```

Reuse an existing plan for fixed-layout or cosmetic edits, with a recorded reason. A complex figure may still require agent wireframe review; this is not automatically another user approval gate. See `semantic-and-layout-gates.md` for reviewer and evidence recording.

## Content Compression

When authoring from prose and content summarization is in scope, compress source text into:

- noun phrases for modules,
- verb phrases for arrows,
- short method labels for algorithm or experiment steps,
- short result labels for validation or findings,
- one-line notes for assumptions, constraints, or limitations.

For replication, frozen labels, or layout-only edits, preserve exact wording and use wrapping, bounds, and spacing. Content compression is not authorization to rename scientific terms or remove evidence.

Prefer 4-8 major modules and 2-5 supporting nodes per major section. Use one dominant reading path and only 1-2 feedback loops unless the source genuinely requires more.

For model-architecture and mechanism figures, compress repeated layers into stage labels such as `CSP block x3`, `Feature fusion`, or `Detect head` instead of drawing every internal layer. Use a legend or caption to explain notation that repeats across the figure.

## Text and Callout Styling

Captions, callouts, legends, and annotation labels follow the base rule in `../drawio/references/docs/design-system/tokens.md` § Text & Label Styling. Two points matter most for publication figures:

- **Transparent, no white box.** Plain text boxes always render `fillColor=none;strokeColor=none;labelBackgroundColor=none` — the base converter enforces this and warns on white fills. A white rectangle behind text occludes the figure and reads as unfinished in a paper; if a label sits on a busy region, prefer a darker font or relocation, and use a `formula` node or shape node with a restrained tint as the deliberate exception — never a hard `#FFFFFF` block.
- **Content-sized boxes.** Size a text/callout box just wider than its longest line, not to a container or source-image region, so captions and callouts stay independently placeable and do not overlap modules or connectors. Vertical CJK labels are one character per line with explicit newlines.
- **Native straight connectors.** Publication figures follow the base edge rules: bound edges only (no arrow-shape stand-ins), collinear no-waypoint orthogonal edges, and bold `endSize=12` open heads (unfilled "V"; block/classic only on explicit request, UML/ER markers keep their own fill); run `--validate --strict` before export.

## Optional Image Preview

Consider an authorized external image-generation preview when it materially helps the requested result, for example:

- complex paper-derived figures with non-obvious layout or hierarchy,
- reference-image redraws where the user wants academic improvement rather than literal replication,
- proposal/thesis/manuscript figures where the user requested a visual composition comparison before YAML work.

Local YAML/SVG preview is sufficient for simple or complex diagrams. Complexity alone does not require external generation or another approval. Resolve the plan under the Diagram Plan Gate and reuse existing semantic decisions; do not equate agent layout review with user approval.

Privacy rules:

- Before sending unpublished papers, confidential reports, proprietary data, or sensitive research content to an external model, verify that existing explicit consent covers the provider and content. Ask only for missing consent; the drawing request alone does not authorize an uncovered sensitive upload.
- Prefer sending the confirmed diagram plan, short labels, layout intent, and visual style constraints instead of raw source documents.
- If the user declines external processing, no image tool is available, or generation fails, fall back to local YAML/SVG preview.

Prompt constraints:

- Request academic diagram style, not a poster or marketing graphic.
- Use white or very light background, restrained colors, thin borders, clear hierarchy, and short labels.
- Ask for boxes, containers, swimlanes, callouts, feedback loops, and orthogonal arrows only when supported by the plan.
- Avoid decorative gradients, stock imagery, icons used as decoration, heavy shadows, and diagonal connector arrows.
- Treat generated text as approximate. Correct exact labels, formulas, and captions in YAML.

## Bundle Contract

Always deliver editable `.drawio`. Select one primary delivery class using `academic-figure-playbook.md § Academic Delivery Matrix` and record it in the figure manifest:

- `raster-publication`: 300ppi-effective PNG; prefer Desktop and use the derivative gate when a local browser renderer is the fallback.
- `vector-submission`: PDF or path-only SVG; apply venue restrictions, including IEEE's PS/EPS/PDF-only rule.
- `draft-preview`: live-text SVG for review while the publication target remains unresolved.

Keep `.spec.yaml`, `.arch.json`, and the manifest in the project-local work directory. Extra user-requested formats are companions, not a reason to change or leave the primary class ambiguous. Never report a live-text SVG as a final Word/LaTeX asset or as an accepted IEEE vector submission.

## Visual Verification

Use exported artifacts for paper-readability checks before any browser path:

Apply the shared preview, structured issue, YAML-first rework, and stopping contract from `../../../drawio/references/workflows/visual-review.md`. This overlay adds the publication checks below; it does not redefine the shared issue taxonomy or runtime.

1. For `draft-preview`, inspect the exported SVG and keep the preview label explicit.
2. For `raster-publication`, inspect the final PNG at 100% and intended page size; a browser-rasterized PNG is acceptable only under the derivative gate with recorded provenance.
3. For `vector-submission`, inspect the exported PDF or path-only SVG and apply the venue acceptance rule.
4. Do not substitute an ad hoc browser or Playwright screenshot for the selected class's artifact. Such screenshots are last-resort review aids, not publication evidence.

For the first exported artifact, check:

- overlap between modules, labels, captions, legends, or formula blocks;
- clipped text or formula rendering issues;
- connector labels sitting on top of lines;
- arrows crossing text or node interiors;
- missing modules, wrong grouping, or visual mismatch from the confirmed plan/source;
- colors being the only carrier of meaning.

If a visible defect is found, adjust the YAML spec and rerender once. Any further correction follows the shared loop limits. Academic review additionally requires A4 readability, caption/legend integrity, formula fidelity, and print-safe meaning before reporting the result.

For a projection drift figure, keep the base runtime and report unchanged.
Publication review must preserve the explicit `[ADDED]`, `[REMOVED]`,
`[CHANGED]`, and `[UNCHANGED]` text, the legend, changed-key evidence, and the
dashed removed relation in grayscale/print output. The academic overlay may
adjust typography and placement only; it must not copy or reinterpret the
snapshot adapter or comparator.

## References

Load these overlay-local academic references for detailed rules:

- `academic-figure-playbook.md` (figure-type pattern library and node budget)
- `academic-export-checklist.md`
- `layout-candidates-and-manifest.md` (candidate, reference-index, and manifest contracts)

Load the sibling base references for shared execution detail:

- `../drawio/references/docs/math-typesetting.md`
- `../drawio/references/docs/design-system/specification.md`
- `../drawio/references/docs/design-system/tokens.md`
- `../drawio/references/workflows/create.md`
- `../drawio/references/workflows/edit.md`
- `../drawio/references/workflows/replicate.md`
