# Evals

Deterministic offline checks run via `python evals/smoke_test.py`; this includes
`test_figure_review.py` and is distinct from the prompt eval set below. New review
contracts have positive/negative fixtures, migration and history checks, context
invalidation, actual-primary-artifact linkage, and a deliberately self-consistent
semantic error that passes structural validation. Synthetic reviewer records in
tests are fixtures, not evidence of real image inspection or reviewer accuracy.
Run a representative actual export and visual inspection separately. No model
effectiveness benchmark has been run by these tests; optional future evaluations
must include correct controls and independently established answers.

`evals.json` is the maintained eval set for this skill; its `version` tracks `SKILL.md`. There is no automated runner: each eval is a prompt plus an assertion checklist, verified manually or by an agent, assertion by assertion.

Historical upstream snapshots are project records under `management/upstream/evals/`; they are intentionally excluded from the runtime skill and install package. To rerun an eval round, use `evals.json` with a fresh session and store dated evidence in the project management area rather than this runtime directory.
