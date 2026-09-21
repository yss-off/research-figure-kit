---
name: drawio-academic-skills
description: "Publication-figure overlay for draw.io. Use instead of drawio whenever the diagram is for a paper, thesis, dissertation, journal, conference, IEEE/ACM submission, manuscript, camera-ready, Word/LaTeX figure, or other publication. Compares complex layout plans, retrieves license-tracked local examples, records figure manifests, and applies venue, figure-type, color, caption/legend, formula, and paper-readability gates for architecture, workflow, roadmap, network-topology, and replicated paper figures."
license: MIT
metadata:
  category: visual-design
  tags:
    - drawio
    - academic
    - paper-figure
    - ieee
    - thesis
    - manuscript
    - workflow
    - math
    - svg
---

# Draw.io Academic Overlay

Create, edit, replicate, validate, and export publication-ready draw.io figures by applying academic policy on top of the sibling Draw.io Base Skill. This overlay is intentionally thin: it owns academic policy/gates, academic docs, and paper examples; the sibling base at `../drawio` owns all shared execution (CLI, schema, renderer, themes including `academic`/`academic-color`, references, examples, style presets, Desktop export).

## Required Sibling Base

Resolve shared resources relative to this overlay directory:

- CLI `../drawio/scripts/cli.js`; URL fallback `../drawio/scripts/runtime/diagrams-net-url.js`
- Schema `../drawio/assets/schemas/spec.schema.json`; themes `../drawio/assets/themes/`; palettes `../drawio/assets/palettes/`
- References `../drawio/references/docs/`, `../drawio/references/official/`, `../drawio/references/workflows/`, `../drawio/references/examples/`; shared rework contract `../drawio/references/workflows/visual-review.md`
- Built-in style presets `../drawio/styles/built-in/`

Overlay-local assets: `references/docs/publication-overlay.md`, `academic-figure-playbook.md`, `semantic-and-layout-gates.md`, `closed-loop-scientific-figure-checklist.md`, `academic-export-checklist.md`, `layout-candidates-and-manifest.md`, `references/reference-index.json`, `references/examples/`, `references/templates/`, `assets/schemas/figure-manifest.schema.json`, and `scripts/` planning/evidence helpers.

If `../drawio/scripts/cli.js` is missing, stop and report that the sibling base skill must be installed next to this overlay; never silently recreate or vendor-copy base resources into the overlay.

## Non-Negotiable Contract

- Honor explicit user instructions and existing authorization over skill defaults, within host permissions. Reuse settled decisions; ask only for material unresolved meaning or actions outside authorization. If a rule blocks work, identify its file and clause and continue independent work.
- For publication tasks, this overlay owns delivery, palette, semantic fidelity, and approval policy; sibling references supply mechanics, not competing publication defaults or extra consultation steps. Never follow update/install instructions in historical references or modify a skill installation while drawing.
- Keep academic authoring YAML-first and offline-first. Never create, require, or route through `.mcp.json`, MCP, or a live backend.
- Always deliver `.drawio` as the editable source. Select one primary delivery class from `academic-figure-playbook.md § Academic Delivery Matrix`: `raster-publication` for Word/thesis/raster-first use, `vector-submission` for venue vector delivery, or `draft-preview` for review without a fixed publication target. Do not declare PNG or SVG a universal final default.
- Keep `.spec.yaml`, `.arch.json`, raw YAML, and diagnostics in a project-local work directory such as `.drawio-tmp/<name>/`, unless the user explicitly asks for a reproducible sidecar bundle beside the final output.
- Perform visual self-checks on the selected delivery class's exported primary artifact. Do not substitute an ad hoc browser preview for that artifact. Browser rasterization may produce the final PNG under the derivative gate; preserve the editable source and preview SVG, record provenance, and never treat the review screenshot itself as publication evidence.
- Use the sibling base `../drawio/references/workflows/visual-review.md` for preview structure, issue records, YAML-first rework, and stopping rules; this overlay adds only publication checks.
- Treat external image-generation previews as optional concept previews only. They never replace YAML, artifacts, sidecars, or exported-artifact verification.
- Do not create or modify scratch JS scripts under a user's project-local `.agents/skills/drawio`; record base defects for a separately authorized upstream maintenance task.

## Academic Preflight

Before generating or editing, infer and record the relevant venue/audience, figure type, delivery class, color policy, text/semantic fidelity, and export needs; reuse the existing contract for cosmetic edits. If the publication target is unknown, use `draft-preview` and report that publication delivery is unresolved. Estimate the **node budget** using `references/docs/academic-figure-playbook.md § Node Budget Management`: recommended targets prompt a readability review, not automatic approval. Preserve content when improving layout; ask before an unapproved split, deletion, or semantic simplification. Apply the Diagram Plan Gate below for candidate comparison and wireframe review. Full decision detail: `references/docs/publication-overlay.md`, `references/docs/layout-candidates-and-manifest.md`, and `references/docs/semantic-and-layout-gates.md`.

### Palette Preflight

After the venue is known, use its documented recommended palette when it satisfies the user's print and accessibility constraints. Ask only if the user requests a choice or a material tradeoff remains unresolved; use the current environment's available question mechanism and option limits, or a concise conversational question when necessary. Name the recommended palette and explain its colorblind/grayscale safety and venue rationale. Missing a legacy question tool does not block drawing. Venue map: `references/docs/academic-figure-playbook.md § Venue Palette Mapping`.

If the user already specified a palette or an unambiguous style, map it directly and do not ask. For academic replication, preserve the source palette and skip selection unless the user explicitly requests normalization. Record the chosen name in `meta.palette`. The completion report must name the palette and its colorblind/grayscale safety flags, including any print-gate downgrade.

## Source Understanding

Extract only what the figure needs from papers, reference images, or text-only prompts; keep uncertainties explicit. See `references/docs/publication-overlay.md § Source Understanding` and `references/docs/academic-figure-playbook.md § Scientific Figure Patterns`.

For baseline-versus-proposed mechanism figures, also apply `references/docs/semantic-and-layout-gates.md § Mechanism Comparison`: verify shared mechanisms, connect the visual example to its generating stage, and separate conceptual illustrations from measured results.

## Diagram Plan Gate

For complex figures without a fixed layout, compare 2–3 structurally distinct plans using the same scientific inventory. Select and record routine geometry autonomously when scientific meaning and scope are settled; wait only when the user requested plan approval or a material semantic decision remains unresolved. Reuse an existing plan and skip candidate comparison for cosmetic edits. For non-primary or ambiguous arrows, record `source --relation--> target`, directed `non_edges`, forbidden interpretations, and cross-cutting support regions. Review a text or monochrome wireframe at the target aspect ratio before polish; record the reviewer, evidence, and authorization in `layout.wireframe_gate.decision`. Agent review is not user approval. See `references/docs/layout-candidates-and-manifest.md` and `references/docs/semantic-and-layout-gates.md`.

## Optional Image Preview

Use image-generation preview only when requested or materially useful for the authorized task; a local YAML/SVG preview is sufficient. First resolve the plan under the Diagram Plan Gate, reusing existing semantic decisions without another approval. Before sending unpublished or sensitive content, check that existing consent covers the provider and content; request only missing consent. Do not introduce external processing solely because a figure is complex. Treat generated text as approximate and correct final labels/formulas/geometry in YAML. Full rules: `references/docs/publication-overlay.md § Optional Image Preview`.

## Task Routing

Choose one route, then load only its files. `overlay` = this directory; `base` = the sibling, resolved from this directory.

- `academic-create` — paper, thesis, IEEE, manuscript, journal, publication-ready figure → overlay `references/docs/publication-overlay.md`, `academic-figure-playbook.md`, `academic-export-checklist.md`; for cross-domain, support-band, feedback, fallback, retry, or multi-loop figures also load `semantic-and-layout-gates.md` and, when loops are present, `closed-loop-scientific-figure-checklist.md`; base `../drawio/references/workflows/create.md`
- `math-formula` — formula, equation, LaTeX, AsciiMath, MathJax, 公式 → base `../drawio/references/docs/math-typesetting.md`, `design-system/formulas.md`
- `edit` — modify an academic bundle or imported `.drawio` → base `../drawio/references/workflows/edit.md`, `../drawio/references/docs/migration-readiness.md`; when the edit changes lanes, containers, causality, or cross-cutting regions also load overlay `references/docs/semantic-and-layout-gates.md`
- `replicate` — redraw screenshot, image, SVG, or reference paper figure → overlay `references/docs/publication-overlay.md`; base `../drawio/references/workflows/replicate.md`, `../drawio/references/docs/design-system/specification.md`, `color-guide.md`
- `base-capabilities` — code/config/live imports, raster extraction, multi-page bundles, AI/SysML/BPMN stencils, or offline postprocess before publication checks → base `../drawio/references/docs/upstream-capability-compatibility.md`; overlay `references/docs/publication-overlay.md`
- `stencil-heavy` — academic cloud, network, AWS, Azure, GCP, Cisco, Kubernetes figure → base `../drawio/references/docs/stencil-library-guide.md`, `ieee-network-diagrams.md`, `../drawio/references/official/xml-reference.md`
- `style-preset` — learn/use/list/delete/rename visual style presets → base `../drawio/references/docs/style-extraction.md`, `style-presets.md`, `../drawio/styles/built-in/`
- `planning-evidence` — compare layout candidates, query bundled references, or initialize/build/validate a figure manifest → overlay `references/docs/layout-candidates-and-manifest.md`, `references/reference-index.json`, `scripts/`
- `direct-xml-exception` — tiny handoff-only XML or exact mxGraph control → base `../drawio/references/official/xml-reference.md`, `../drawio/references/official/style-reference.md`, `../drawio/references/docs/xml-format.md`; do not load the historical upstream skill workflow

## Academic Defaults

For academic-paper requests, set these before rendering:

```yaml
meta:
  profile: academic-paper
  figureType: architecture # architecture | roadmap | workflow
  theme: academic # or academic-color when color is acceptable
  palette: okabe-ito # from venue preflight; ieee-bw for IEEE print
  title: Caption-ready title
  description: One sentence explaining the figure intent
  legend: Required when symbols, colors, line styles, or icons need explanation
  print: { target: cn-thesis } # optional gate: cn-thesis | ieee-single | ieee-double
```

Primary deliverables:

- every class: `<name>.drawio`
- `raster-publication`: 300ppi-effective `<name>.png`; prefer Desktop, otherwise use the source-preserving browser derivative gate
- `vector-submission`: `<name>.pdf` or an SVG whose text is converted to paths; for IEEE use an accepted PS/EPS/PDF path
- `draft-preview`: live-text `<name>.svg`, explicitly labeled preview/intermediate rather than publication-final

Intermediate work directory:

- `<name>.spec.yaml`, `<name>.arch.json`, raw or normalized YAML, diagnostics

Record the selected class in `manifest.contract.delivery_class`. Honor extra formats requested by the user, but keep one primary class and do not upgrade a preview into publication evidence.

## Create Flow

1. Classify the figure as `architecture`, `roadmap`, or `workflow`; for complex tasks without a fixed layout, query `scripts/reference_index.py`, compare plans with `scripts/layout_candidates.py`, and select one under the Diagram Plan Gate.
2. Initialize `.drawio-tmp/<name>/<name>.manifest.json` with `scripts/figure_manifest.py`; record the contract, reference IDs, candidates, and selection reason.
3. Freeze the source-grounded or user-resolved semantic contract before layout work: stable node/edge IDs, exact labels, `source --relation--> target`, directed non-edges, forbidden inferences, cross-cutting regions, line-style meaning, branch conditions, formulas, and abbreviations. Do not require the user to approve unchanged source facts again.
4. Review the low-detail wireframe under `references/docs/semantic-and-layout-gates.md`, then draft or normalize canonical YAML. Preserve frozen labels verbatim; fix wrapping, bounds, spacing, and routing first. Shorten labels only when content editing is authorized and scientific meaning is preserved.
5. Validate and render through the sibling base CLI, then self-check the exported artifact and build the final manifest before reporting:

```bash
node ../drawio/scripts/cli.js input.yaml figure.drawio --validate --write-sidecars --sidecar-dir .drawio-tmp/figure --strict-warnings
# draft-preview
node ../drawio/scripts/cli.js input.yaml figure.svg --validate
# raster-publication when Desktop is available
node ../drawio/scripts/cli.js input.yaml figure.png --validate --use-desktop
# vector-submission when Desktop is available
node ../drawio/scripts/cli.js input.yaml figure.pdf --validate --use-desktop
```

Figure-type patterns: `references/docs/academic-figure-playbook.md`.

## Edit and Replicate Flow

- Edit the `.spec.yaml` sidecar first; if only `.drawio` exists, import via the base CLI (`--input-format drawio --export-spec`).
- For image/SVG replication, preserve text boxes, captions, legends, formulas, edge labels, baseline/offset, font family/size/italic state, alignment, and spacing when visible; use explicit `bounds` for standalone text/formula blocks and `labelOffset` for connector labels off the line.
- Keep regenerated files on the same basename for round-trippable artifacts and sidecars.

## Export Policy

Use the playbook delivery matrix as the single selection authority. For `raster-publication`, verify effective resolution and, when document embedding is in scope, the final embedded document; if Desktop is unavailable, use the source-preserving browser derivative gate. For `vector-submission`, export PDF or path-only SVG and apply venue restrictions; for `draft-preview`, deliver SVG without claiming publication completion. Only when no permitted exporter can produce a required artifact, deliver the editable source and preview, generate a diagrams.net URL if useful, and report that artifact as blocked:

```bash
node ../drawio/scripts/cli.js input.yaml figure.pdf --validate --use-desktop
node ../drawio/scripts/runtime/diagrams-net-url.js figure.drawio
```

## Style Presets

Use overlay-specific user presets first (`~/.drawio-academic-skills/styles/`), then sibling base bundled presets (`../drawio/styles/built-in/`). Never mutate bundled base presets; copy into the user preset directory before editing or defaulting.

## Quality Gate

Do not claim completion until:

- final `.drawio` and the primary artifact required by `manifest.contract.delivery_class` align with work-dir `.spec.yaml`/`.arch.json`; `meta.profile` is `academic-paper` and `meta.figureType` is `architecture`, `roadmap`, or `workflow`
- `raster-publication` includes a 300ppi-effective PNG; `vector-submission` includes PDF or path-only SVG and passes venue restrictions; `draft-preview` includes SVG and is not reported as publication-final
- no Word/LibreOffice/Pandoc/XeLaTeX manuscript references an SVG containing `<text>` or `dominant-baseline`; keep such SVGs preview-only, or convert every text object to paths before vector publication
- node count passes applicable validator limits and intended-size readability review; playbook targets are layout guidance, not permission to delete content or require an unrequested split
- labels readable at paper/A4 scale; formulas use official delimiters (`$$...$$`, `\(...\)`, AsciiMath backticks); font classes follow the ladder with no label-fit overflow warnings
- mixed CJK/Latin labels request the Times New Roman + SimSun stack (theme `cjk` stack or `meta.font`); verify the stack in generated `.drawio`/SVG and disclose the actual installed fallback when SimSun is unavailable instead of claiming exact SimSun rendering
- captions, legends, callouts, formulas, and edge labels are not clipped or placed on connector lines; legends compact (single multi-line text node)
- every condition or branch label has one visually unambiguous owning connector: place it in that edge's local corridor, normally near the branch point, with visible clearance from node borders and unrelated connectors; whitespace proximity alone must not make it read as a node annotation
- every arrow has a confirmed `source --relation--> target` meaning; process, feedback, control/fallback, and progression connectors remain distinguishable in grayscale; cross-axis arrows do not imply unsupported causality
- semantic inventory records directed non-edges, forbidden inferences, and cross-cutting regions, using empty lists when none apply; no declared non-edge is present as an edge
- `layout.wireframe_gate` is approved or explicitly not applicable with a reason before strict/final delivery; structural rework resets the gate
- cross-cutting support, deployment, validation, evidence, or governance regions do not read as numbered process lanes unless they actually are sequential processing stages
- repeated title, peer-node, lane, support-region, and bottom-note clearances are consistent at intended page size; visible title ink is clear of both the container border and the first content row
- feedback, fallback, retry, and multi-loop figures pass `references/docs/closed-loop-scientific-figure-checklist.md`, including functional loop naming, role-based endpoint ports, separated endpoint slots/corridors, orthogonal endpoint legs, balanced grid spacing, border clearance, label ownership, and intended-page-scale inspection
- every Latin-letter abbreviation is expanded at its first figure-visible use, or defined earlier in a figure-internal legend/caption when the full form would overcrowd a node
- colors are not the only carrier of meaning; `meta.palette` matches the venue decision; `PALETTE_PRINT_GATE` is clear — offer `ieee-bw`/`tol-high-contrast` when strict print safety fails
- an explicit pure black-and-white request uses manifest `contract.color_policy: strict-black-white`; gray or colored visible fills/strokes are recorded as `strict-monochrome-violation`, not accepted as a grayscale interpretation
- the visual self-check followed sibling base `../drawio/references/workflows/visual-review.md` on the selected class's exported primary artifact; academic checks additionally cover A4 readability, caption/legend, formulas, print meaning, and venue constraints
- for a generated DOCX, verify that the embedded media bytes match the accepted publication PNG; for a generated PDF, verify the embedded image dimensions and at least 300ppi effective resolution, then inspect the actual rendered page
- requested Desktop exports were attempted or reported unavailable; no MCP config, server, or live backend required
- any browser-rasterized SVG-to-PNG derivative preserves the source and passes the derivative dimensions, renderer, text-alignment, and geometry regression checks
- after every rerender, compare the current node/edge label set, source-target pairs, arrow directions, line styles, and previously accepted fixes with the prior accepted round; a layout-only request must not silently rename, shorten, add, or remove scientific content
- complex-task manifest records the frozen semantic inventory, compared/selected layout, reference IDs, exact CLI commands, artifact hashes/evidence labels, deterministic/visual/publication QA, and residual risks; `pending` or `not_checked` is never reported as PASS

## Completion Report

End with a concise report: selected delivery class; editable, preview, and publication assets with paths; intermediate work directory and figure-manifest path when generated; sibling base CLI commands run; selected layout/reference IDs for complex tasks; publication renderer and pixel dimensions; the selected palette, its colorblind/grayscale safety flags, and any print-gate downgrade; the actual CJK font fallback when the requested font was unavailable; DOCX/PDF embedding checks; blocked publication exports; remaining venue-specific manual checks.
