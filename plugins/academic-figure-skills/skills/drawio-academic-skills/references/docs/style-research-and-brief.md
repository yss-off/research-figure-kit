# Research the style before drawing

The outcome is a figure suited to the current task, with a clear reading order and readable details at its real delivery size. A journal label, a default theme, or successful XML validation does not establish visual quality.

## Research first, then author

For each new figure or substantial restyling:

1. Identify the communication goal, audience/venue, figure type, medium, target width, and already-confirmed scientific inventory. Separate appearance from unresolved scientific meaning.
2. Find close visual precedents: normally a small set of actual figures from comparable work, prioritizing the same task and venue over famous but unrelated designs. Check applicable official graphics guidance separately. Verified local sources are useful; permitted browsing supplies missing current evidence. Do not infer style from abstracts or reuse the same papers irrespective of the task.
3. Inspect actual figures at page/print scale. For each, record source URL or local path, version/date when known, figure/page locator, what was actually inspected, useful features, and features to reject. A metadata-only source cannot support a claim about its visual appearance.
4. Convert observations into a concrete style brief: reading axis, grouping, visual hierarchy, shape vocabulary, restrained palette with semantic roles, font ladder at target size, line/arrow treatment, whitespace, caption/legend placement, and intended output. Explain why this combination suits the current content. Defaults are design choices, not journal mandates.
5. Use the brief before wireframe and final authoring. Discuss first when the user explicitly requests that checkpoint; otherwise make ordinary reversible appearance choices within authorization. Retain approved scientific relations. A cosmetic request does not authorize deletion, new claims, changed arrows, or a new model architecture.

For small revisions, verify that an existing brief still fits the task and reuse it. Refresh research when the task, venue, medium, or figure type changes, or aesthetic rejection reveals the brief did not fit. If current external sources cannot be accessed, use inspected local precedents where possible and label remaining assumptions provisional; do not pretend research was completed or add a network dependency to the renderer.

## Brief record

Store a short Markdown or YAML brief in `.drawio-tmp/<name>/style-brief.*`. For complex figures, add its path to `manifest.contract.style_brief` and optionally put observation-only source records in `manifest.reference_selection.style_sources`. Existing manifest object fields accept these records; they are not automatically enforced or graded by the manifest validator.

Minimum useful record:

- task, audience, figure type, intended width, and unchanged scientific contract;
- inspected source/version/figure locator and evidence boundary (actual figure vs metadata only);
- adopted and rejected visual features, with reasons;
- selected composition, font/size, palette/roles, connectors, spacing, and caption treatment;
- applicable official rules vs local recommendations or provisional assumptions;
- how the rendered figure will be checked at delivery size, including grayscale when relevant.

## A TWC network overview example

This is a researched starting point for a protocol-wise time-frequency occupancy model, not a universal TWC style:

- White background, lightly grouped feature/query branches, and a clear input-to-output axis.
- Ordinary inherited modules stay neutral; two focal mechanisms use restrained blue/vermillion accents plus explicit labels. Palette `ieee-color` is a bundled local starting point, not a TWC official palette.
- Simple flat feature planes and query tokens may explain tensors better than another prose box; schematic shapes must not imply measured outputs, false dimensions, or extra computation.
- Route intermediate attention feedback separately; preserve the established solid-feedback/dashed-initialization meanings. Pretraining sits outside sensing inference.
- At a roughly 182 mm double-column width, 9–10 pt main labels and 8–9 pt secondary labels are useful local design targets. They are not a verified TWC-specific minimum. Move long explanation to the caption when content editing is authorized; avoid an oversized in-figure title.
- Avoid decorative shadows, gradients, artificial perspective, excessive saturated colors, and long vertical labels. A low-detail monochrome wireframe tests structure and does not count as finished styling.

Observed sources in the initial research pass (2026-10-02):

| Source/version and actual locator | Adopt | Avoid or boundary |
| --- | --- | --- |
| [Zhao et al., TWC 2025, DOI 10.1109/TWC.2025.3535807](https://openresearch.surrey.ac.uk/esploro/outputs/journalArticle/A-Transformer-based-Self-supervised-Learning-Framework/99960765902346?institution=44SUR_INST), repository author PDF, file page 6 / printed page 5, Fig. 3–4 | Light stage containers, small spectrograms, distinct parameter-sharing connection | MAE masking and detection are not the current occupancy method |
| [Wu et al., CDDM author version, arXiv:2309.08895v1](https://arxiv.org/pdf/2309.08895v1), p. 3 Fig. 2; published TWC DOI 10.1109/TWC.2024.3379244 | Main path plus grouped local detail | Many saturated fills and small sub-blocks; no claim author PDF equals final publisher graphics |
| [Lee et al., arXiv:2409.03924v2](https://arxiv.org/pdf/2409.03924v2), p. 6 Fig. 2–3; published TWC DOI 10.1109/TWC.2025.3600286 | Consistent operation encoding and separate conditioning paths | Dense colored layers and vertical text are unsuitable for this overview |
| [Cheng et al., Mask2Former, arXiv:2112.01527v3](https://arxiv.org/pdf/2112.01527v3), p. 3 Fig. 2, CVPR 2022 | Compact feature/query glyphs and overview/detail hierarchy | Method-adjacent, not a TWC example; do not copy its class head or object-query semantics |

Official sources: [IEEE Author Center graphics](https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-graphics-for-your-article/) stresses redundant color/shape encoding and grayscale interpretation; [Proceedings of the IEEE guidelines](https://proceedingsoftheieee.ieee.org/resources/guidelines-for-figures-and-tables/) recommends consistent typography/spacing, approximately 9–10 pt lettering, and restrained color/decorations. The latter is another journal's guidance, not a TWC-specific mandate. Check [TWC policies](https://www.comsoc.org/publications/journals/ieee-twc/policies-guidelines) for the actual target requirements. Research observations do not guarantee acceptance.

These sources are observation-only: their artwork is not bundled, relabeled MIT, or reproduced. Public access is not reuse permission; review licensing separately if an actual asset is to be reused. Borrow abstract design principles, not scientific labels, branded assets, or protected compositions.

For TWC model architecture tasks, continue with [TWC model diagrams](twc-model-figures.md). It records updated IEEE source distinctions, inspected encoder/decoder and diffusion-model precedents, and specific composition/route-readability checks. Reuse its evidence when task-matched; do not treat the example layout as universal.

## Review the style, not just the file

After rendering, inspect hierarchy, alignment, balanced whitespace, label wrapping, compact legends, local detail density, and visual distinction between features/parameters/operations. Compare against the brief at target size and in grayscale as applicable. Existing automated checks establish only their declared properties. Keep structural correctness, visual self-review, publisher requirements, and user acceptance separate; do not report a palette flag or schema PASS as proof of aesthetics or accessibility.
