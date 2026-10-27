# Review contract: manifest 1.1 and figure.review.json 1.0

This offline contract checks evidence associations and recorded decisions. It
does not prove careful review, scientific correctness, or reduced reviewer error.
It applies only to this academic Draw.io overlay. Python data plots retain their
own workflow. No external reviewer, model, service, or network is mandatory.

## Authoring and source correspondence

Before drawing, identify the figure's intended claim and abstraction level.
Initialize a pending review after initializing the manifest:

```bash
python scripts/figure_review.py init figure.manifest.json --output figure.review.r1.json
```

The command writes a pending record and reports its path/hash. Set
`qa.review = {path, sha256, schema_version: "1.0"}` in the manifest. Use absolute
file paths, including `render.canonical_spec` and `qa.scientific.sources`.
Keep review files outside `render.artifacts` and scientific sources; they are
referenced separately to avoid circular hashes. All output commands refuse
implicit overwrite. A review record must never overwrite its inputs.

Set `scope` to `implementation` only when actual implementation is reviewed.
Scientific sources have explicit `kind`: `code`, `configuration`, `method`,
`approved_contract`, or `data`. Implementation scope requires a code source;
conceptual scope can use an explicit method or approved non-empirical contract.
A missing implementation cannot be replaced by an invented approved contract.
When code and a method disagree, report the discrepancy rather than silently
choosing a scientific authority.

Each claim has a stable `id`, `object_ids`, `statement`, `sources` (path and
function/paragraph `locator`), `simplification`, `status`, and `comparison`.
Cover declared node and edge IDs exactly; one claim can group related objects.
Pure decoration should not be a semantic node in the first place. For a support
region, say explicitly that it is non-causal. Compare sources back to the figure
as well: inventory coverage alone cannot find operations omitted from both the
inventory and the table. Record each claim's actual source comparison, not only
"pass". An explicitly recorded omission can still be misleading and need repair.
LN placement, projection visibility, and parameter initialization endpoints are
task-specific. Partial parameter transfer must not imply full-module transfer.

Store the actual caption text in `contract.caption`. Store physical width in
`contract.review_width_mm` when known. These are part of the reviewed context.
For unfixed draft previews, use null width and explain the viewing limit; never
turn that into a publication-readability claim.

## Read, then compare

Inspect the actual delivered primary artifact and caption before comparing the
reading with the claims table. Record `readback.observations`: input/output,
main path, line meanings, and inset correspondence (or an explicit no-inset
explanation). Also record a concrete `visual_assessment` and `viewing` mode,
width and reason. Inspect the complete figure and follow affected routes at
intended size, then magnify details as needed. A crop or enlarged view alone is
not sufficient. Publication viewing width must match the contract and geometry
scene's physical width.

Use `method: informed_self_check` for an author who knows the implementation.
`isolated_context` means the reviewer received only artifact, caption and audience,
and `inputs` must say exactly that. Other inputs can include `design_context`,
`claims` and `code`; these disqualify an isolated-reading claim. Use
`independent_reviewer` with accurate reviewer/input metadata for other reviews.
These labels record provenance, not proof of actual cognitive independence.
Extra independent review is optional. Do not add a new approval gate.

Classify discrepancies as `defect`, `allowed_abstraction`, `reviewer_error` or
`pending`, with a reason. A confirmed defect references its issue ID. A reading
discrepancy is an investigation lead, not automatic evidence that the figure is
wrong. Unknown evidence remains pending/not_checked rather than not-applicable.

## Issues and repair rounds

`issues` retains discovery `id`, `object_ids`, category (geometry/scientific/visual),
problem, evidence, and ordered events. Each event records `state`, `decision`,
`verification`, `context_sha256`, and artifact path/hash references. The digest
is `context_digest(current_context(manifest))` from the helper. History starts
with `open`; `fixed` means edited but not verified. Only `closed` and `not_defect`
resolve issues, and both require a concrete current verification and at least one
current delivered artifact. "Not fixing a confirmed defect" is still unresolved.
After resolution, reopen with an `open` event before another repair.

`qa.visual.issues` contains current unresolved visual items with matching `id`s,
not the historical log. A hidden open/fixed issue blocks final acceptance even
if someone clears this array. Closed issues remain in the review record.
For imported legacy findings without IDs, preserve their information and assign
stable IDs when incorporating them into the new history; do not invent old
verification events.

After rendering a changed revision:

```bash
python scripts/figure_review.py start-round figure.manifest.json figure.review.r1.json --output figure.review.r2.json
```

This preserves claims and issue history, binds the new context, resets claim
comparisons and readback to not_checked, and links the prior review by hash.
Previous review files must remain available. Linked issue history cannot be
deleted or rewritten; append events and current rechecks instead. For unchanged
judgments, explain why they still apply and explicitly re-record them against
the new context. Do not merely replace hashes. This is not a tamper-proof ledger:
a self-consistent false statement still needs scientific review.

## Invalidation and delivery

The context binds the full contract (including caption/width), semantic inventory,
canonical spec, delivered artifacts, actual reviewed artifact, scientific basis,
and source files/kinds. Changed inputs invalidate the old record. Scientific
SVG bindings and geometry replay remain independently required. Review-file
hashes do not refresh during manifest build; edited records must be deliberately
inspected and rebound. Current closure events must be rechecked after context
changes. Initializing or starting a round never generates a pass judgment.

Accepted or strict manifests require version 1.1, a current review reference,
complete claim coverage and source comparisons, actual-artifact reading and
visual assessment, no pending discrepancies, no unresolved issues, and the
existing geometry/scientific/visual/publication requirements. Unsupported
geometry still blocks acceptance. Optional independent review may be absent.
Diagnostic previews may retain warnings without claiming acceptance.

```bash
python scripts/figure_manifest.py migrate legacy.manifest.json --output figure.manifest.json
python scripts/figure_manifest.py validate figure.manifest.json --strict --verify-artifacts
```

Migration copies only a legacy 1.0 manifest, retains old issues and evidence,
downgrades to review, resets visual/scientific status, and never overwrites the
input or approves missing new reviews. Initialize and complete a new review.

## Verification boundary

Use `evals/test_figure_review.py` for deterministic contract regressions. Include
positive and negative fixtures and a self-consistent semantically wrong claim
that the contract cannot detect. The local validator implements only the
keyword subset used by the shipped review schema and fails on unknown keywords;
it is not a general JSON Schema implementation and adds no dependency.

Run actual export/inspection separately from those fixtures. Any future isolated
model-effectiveness evaluation needs pre-checked answers, correct controls,
fixed captions and sizes, and separate detection/miss/false-positive/unknown
results. Until measured, report "review effectiveness not measured". Contract
PASS and one inspected figure are not evidence of a reduced miss rate.
