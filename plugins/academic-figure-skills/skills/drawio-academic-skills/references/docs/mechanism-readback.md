# Mechanism figures: make the intended reading observable

Use for implementation-backed model figures, overview/detail compositions, or
repeated complaints about meaning, label ownership or routes. Reuse settled
source facts and style decisions for small edits. This is not an extra approval
gate or a requirement to redraw every module in source-code detail.

## Before layout: distinguish facts, abstraction and reader questions

First name the selected implementation/configuration version and each panel's
explanation task. For code-backed diagrams, trace relevant input, operations,
conditioning, output, loss and transfer endpoints **from source to figure**,
then check each drawn object **back to source**. Inventory coverage alone misses
an operation omitted from both the inventory and the drawing. In existing
`claims[].comparison` record the reverse check; in `simplification` state what
is grouped, omitted or split out of a code module and why. A visual convenience
must not invent an executable operation. Keep implementation discrepancy and
allowed abstraction separate.

Turn consequential ambiguities into a small set of questions in the existing
manifest contract, bound to stable object IDs. For example:

```json
"reader_questions": [
  {"id": "identity", "question": "What is fixed and what can be learned?",
   "object_ids": ["queries"]},
  {"id": "detail", "question": "Which overview object is expanded here?",
   "object_ids": ["layer", "detail"]}
]
```

Adapt questions to the task: two feature paths, input/output identity,
parameter-transfer scope, or predicted versus illustrative imagery. Do not turn
these examples into mandatory protocol names or a generic checklist on every
figure. After viewing the export and caption, record answers under
`readback.answers` as `{id, observation, status}`. Status is `not_checked`,
`review`, `blocked` or `pass`; observations describe visible evidence and any
caption dependence. Do not answer by silently importing code knowledge.
Ambiguities remain issues until fixed or justified. The helper checks answer
coverage/currentness, not the truth or quality of an answer.

The field is optional for legacy and simple figures. When declared, every
question needs exactly one current, nonempty passing answer for strict review.
Changing the questions changes the reviewed context. New rounds start with no
answers; neither an initializer nor geometry PASS supplies them.

## Layout decisions that survived the case review

- Use consistent object names/shapes to connect overview and detail. The inset
  must identify the actual subcomponent, not merely its enclosing stage. View
  the complete composition before polishing a local panel.
- Label an edge through supported native edge-label placement when feasible;
  otherwise record its owning edge in the claim/route evidence. Inspect competing
  nearby routes, not only collision clearance. A floating Q/K/V-style annotation
  must not require the reader to guess ownership.
- Check attachment face, port slot, full route and landing segment separately.
  For an unconstrained single port, a face-centred placement is a useful default,
  not a universal rule. Offset slots can be correct for multiple inputs,
  residuals or obstacle avoidance. Fixed attachment does not imply centred or
  clear attachment.
- Compare direct and bent routes subject to scientific grouping, spacing and
  the user's frozen layout. A shorter line is worse if it crowds inputs or
  detaches labels. Retain justified residual/feedback routes. No bend-count or
  centre-alignment threshold is a publisher requirement.
- Declare the role of embedded examples in `provenance.sources` and the claim
  comparison: prediction, ground truth, conceptual illustration or independent
  appearance reference. Separate examples cannot establish a same-input output
  correspondence. Do not manufacture protocol morphology. Source attribution,
  usage rights and scientific representativeness are separate checks.
- Keep the caption focused on panel roles, symbols and indispensable reading
  conditions. Detailed implementation explanations belong in the manuscript;
  internal review limitations belong in delivery evidence. Essential distinctions
  such as illustrative versus predicted must remain available to the reader.

## Revision and delivery

Use the existing review lifecycle, not a second issue ledger. Preserve the
previous review file. Before a revision, record permitted changes and settled
constraints in the work notes; after it, compare the actual changed objects,
routes, labels and previously resolved issues. Inspect the full figure at the
declared width as well as the affected detail. Use:

```bash
python scripts/figure_delivery.py figure.manifest.json \
  --previous-review figure.review.r1.json --output delivery.r2.json --strict
```

The command always replays strict manifest checks. `--strict` exits 1 for
incomplete evidence; malformed inputs exit 2. Without it, diagnostic report
creation can exit 0 while JSON still says `needs_review`. Always read JSON.
`revision` compares the preserved prior context with current files and declared
inventory. It does not infer geometry changes from a spec hash, prove unchanged
scientific meaning, or authorize scope expansion. Use `figure_review.py
start-round` to preserve history and reset judgments; complete the new review
and bind it normally. A report never writes PASS into a manifest or closes issues.

Report five layers separately: structure/export, replayed geometry,
scientific evidence, actual-artifact readability, and publication checks.
`evidence_complete` means the recorded contract is complete, not that a figure
is beautiful, scientifically correct, accepted by its author, or publisher-ready.
Publication checks accept nonempty observation strings or objects with nonempty
`name`, `evidence` and `status: pass`. Null, blank, malformed or unresolved entries
remain incomplete even when the layer flag says pass.
Publication checks must be recorded even for a preview (describe the preview
delivery check, not a fictitious venue approval). A diagnostic preview remains
deliverable with its unresolved layers clearly disclosed.

## Basis and boundaries

- [draw.io fixed/floating connectors](https://www.drawio.com/docs/manual/connectors/connector-fixed-vs-floating/)
  distinguishes stable attachments from movable perimeter attachments.
- [draw.io connector labels](https://www.drawio.com/docs/manual/connectors/connector-labels/)
  documents labels attached to and moving with a connector. Desktop behavior
  is not proof of bundled exporter parity; verify the actual export.
- [Graphviz external labels](https://graphviz.org/docs/attrs/xlabel/) treats
  labels separately from routing and can omit labels it cannot place without
  overlap. This motivates checking label completeness as well as clear space;
  it does not introduce Graphviz as a dependency.
- [Guidelines for Human-AI Interaction, CHI 2019](https://www.microsoft.com/en-us/research/project/guidelines-for-human-ai-interaction/)
  supports disclosing capability/error boundaries. Layered delivery is our
  application of that principle, not a proven reduction in figure-review errors.
- [CheckList, ACL 2020](https://aclanthology.org/2020.acl-main.442/)
  motivates capability-focused behavioral tests. Paired figure defects,
  valid controls and revision invariance are our adaptation; the paper does
  not validate this plugin or visual review.

These are engineering/design references, not TWC mandates. Rendering remains
offline. See `evals/mechanism-review-cases.json` for anonymized paired cases and
the limits on interpreting their results.
