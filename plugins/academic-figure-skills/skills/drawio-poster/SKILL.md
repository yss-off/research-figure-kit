---
name: drawio-poster
description: "Create, revise, or review branded service-flow posters and customer-facing decision guides for chat sharing, mobile viewing, or print, using editable draw.io. Use for posters whose core is a process or conditional choice, including logo integration and short explanatory notes. Do not use for publication figures, numerical plots, generic software diagrams, or illustration-led campaign posters."
license: MIT
metadata:
  version: "0.1.0"
---

# Branded flow posters

Use this overlay for customer-facing process posters. It owns hierarchy, concise copy and viewing-size review; the sibling `../drawio` owns YAML, connectors, rendering and export. Read its `SKILL.md` for the requested authoring/edit route. Publication figures go to `../drawio-academic-skills`; quantitative plots go to `../scientific-visualization`.

## Preserve the task

- Discussion and review are read-only until changes are requested. During creation, make ordinary reversible choices without repeatedly asking for approval. If the user requests a sample first, label it as a sample and identify content deferred from the full poster.
- Separate **confirmed meaning**, **visual preferences**, and **open content questions**. Treat the latest correction as a patch, not a reason to restart the design or lose earlier accepted conditions. Keep pricing/units, branch meanings, dates and exceptions explicit; never silently turn a cost explanation into a blanket price or a service objective into a guarantee.
- User-provided claims are copy inputs, not verified official facts. Do not invent official endorsement, availability dates, service duration or future prices. Preserve supplied caveats; research claims only when requested or needed to answer a factual question. If references contain conflicting copy, the user's current instructions win.
- Preserve a chosen flowchart when polishing it. Cards suit comparison; branches suit conditional choice. Do not replace one with the other solely to make the page look cleaner.

## Compose before polishing

Determine the intended viewing width or print size from context. In ordinary chat sharing, a 390–432 px preview is a useful **test assumption**, not a universal canvas size. Confirm where the eye should go: title → applicable condition → outcome/action; notes explain or qualify and should not compete with the flow.

When no composition is settled, sketch two materially different arrangements with the same content inventory, then select a sensible one. Do not impose a new approval gate. Reuse accepted geometry for local copy edits. After repeated aesthetic rejection, diagnose hierarchy, density and viewing scale before another cosmetic change.

- Balance branch density. Do not stretch a shallow branch merely to align outcomes if the resulting empty space shrinks important text. Alignment, side-by-side results and inline prices are design options, not invariants.
- Use consistent, modest rounding, fills, margins and line weights. Do not force every phrase into a box or remove every box. Distinguish conditions from results through grouping and typography; maintain bound native connectors.
- Match the logo's palette intentionally. Keep the supplied logo intact, proportional and readable with clear space. Do not insert a full reference screenshot as the poster, draw a replacement logo, or assume an uploaded raster is a vector original.
- If a brand/site style is requested, inspect primary references and translate specific features into hierarchy, spacing, typography and surface treatment. A famous brand name or a contrast score is not evidence that the resulting poster looks good. Never add the reference brand's identity as an endorsement.

## Copy and local revisions

Read `references/poster-review.md` when deciding hierarchy, reviewing a poor result, or handling repeated revisions. Use short conditional labels, explicit actions and consistent units. A note can be one grammatical sentence across multiple visual lines; do not turn automatic wrapping into separate paragraphs.

For small revisions, reread the current canonical YAML and patch stable IDs, labels and affected bounds. Preserve the source logo and unaffected branches. Regenerate from that source; avoid a fresh bespoke build script or a new version directory for every wording change. Keep user-requested snapshots, but do not delete previous work without authorization.

Text must fit the **actual font and output scale**. `scripts/poster_tools.py wrap` measures a supplied font via Pillow and protects Latin/model tokens and explicit `--keep` phrases. Recompute wrapping when wording, font, font size or box width changes; remove obsolete hard line breaks only when that paragraph edit is intended. It suggests display lines; it does not change canonical wording automatically.

## Verification and delivery

Use the base export path and inspect the exported artifact. Use the actual SVG viewBox or raster width, not a guessed YAML canvas, because export padding/cropping may change the scale. `scripts/poster_tools.py audit` reports nominal displayed font sizes from uncompressed single-page Draw.io XML and a declared source width. Mark primary/secondary text using exported cell IDs; unknown roles or font sizes remain unresolved.

Primary/secondary minimums are configurable review thresholds, not WCAG requirements. Read the main conditions, prices and deadlines at target size; do not claim “one glance” readability when they only become legible after zooming. Check note dominance, branch-label attachment, unexpected wraps, number/unit collisions and logo balance separately from file integrity and contrast.

Separate the evidence:

1. Content: confirmed conditions, actions and exceptions preserved.
2. Geometry/file checks: schema/XML/export integrity and measurable scale/fit.
3. Visual judgment: hierarchy, balance and readability in the exported preview.
4. User acceptance: only when the user actually accepts; an internal review is not a user test.

Deliver the editable `.drawio` and the requested image, with sidecars and review results in `.drawio-tmp/<name>/`. Use base fallback rules when Desktop is missing and name the exporter actually used. Record renderer defects for upstream maintenance; do not copy patches into this overlay, silently suppress warnings, or change installed skills during a drawing task. Stop when the authorized result and relevant checks are complete.
