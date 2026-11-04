# Three-layer figure review

Review the delivered rendering, not only the plotting code. Keep numeric, textual, and visual evidence separate so that a good-looking image cannot hide a scientific error.

## Layer 1: Numeric mapping

Compare the figure with the source data and declared transformations.

- Verify that plotted values, category order, group membership, and panel assignments match the data used.
- Verify axis transforms, limits, reference baselines, bins, smoothing, normalization, and missing/excluded observations.
- Verify estimator, uncertainty definition, `n`, and independent replication unit.
- Verify that paired, nested, repeated, or time-ordered observations are encoded as declared.
- For sampled, aggregated, or rasterized views, record what information was reduced and how.

This layer normally requires data/code comparison. Pixel inspection alone cannot pass it.

## Layer 2: Textual semantics

- Check every axis label, unit, legend entry, panel label, annotation, and scale-bar label.
- Check that caption and figure use the same variable names, groups, uncertainty terms, and abbreviations.
- Check that missing, excluded, modeled, and interpolated values are described consistently.
- Check for missing glyphs, fallback fonts, broken math, minus signs, superscripts, and CJK characters.
- Do not add statistical significance labels unless the analysis and correction method were supplied and confirmed.

## Layer 3: Visual geometry at final size

Render a PNG preview at the intended physical size and inspect it directly.

- No clipping, text collisions, hidden data, legend occlusion, or panel overlap.
- Labels and critical marks remain legible at final size.
- Panel labels and shared axes are aligned; common variables keep the same color, marker, unit, and scale where comparison requires it.
- Color is not the only cue; grayscale and contrast screens are supporting evidence, not accessibility certification.
- Missing/out-of-range values remain visible and distinct.
- The visual hierarchy supports the intended claim without exaggerating it.

Use `scripts/visual_qa.py` for deterministic glyph, canvas-boundary, and tick-overlap checks. Then inspect the rendered preview manually or with an image-capable model. Automated PASS does not pass this layer by itself.

## Bounded revision loop

1. Render a fresh preview.
2. Run deterministic checks.
3. Review numeric, textual, and visual layers separately.
4. Make the smallest source-level correction.
5. Re-render and re-run all affected checks.

Finish when all required checks pass. After two correction rounds, reassess the evidence and approach; continue authorized, reversible repairs while a concrete improvement path remains. Stop the blocked portion when repeated attempts make no progress, a new scientific choice is required, or further work exceeds authorization or the agreed budget. Continue independent work and report:

- unresolved issue;
- affected layer and artifact;
- evidence observed;
- correction attempts already made; and
- the user or analysis decision needed.

Never edit the rendered bitmap to conceal a source-level problem. Do not weaken axes, omit data, or change transformations merely to make a check pass.

## Review record

```yaml
numeric:
  status: pass | review | blocked | not_checked
  evidence: []
textual:
  status: pass | review | blocked | not_checked
  evidence: []
visual:
  status: pass | review | blocked | not_checked
  evidence: []
revision_rounds: 0
residual_risks: []
reviewed_artifacts: []
```

`not_checked` is preferable to an unsupported PASS.
