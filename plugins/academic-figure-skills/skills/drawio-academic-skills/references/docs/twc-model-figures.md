# TWC model diagrams: evidence-backed design and review

Use this reference for TWC/IEEE wireless model architecture figures, especially Transformer encoder/decoder networks with conditioning, residual paths, overview panels and local block expansions. It is a task-matched design guide, not an official TWC style specification or an acceptance certificate. Preserve an already-approved scientific graph and composition when applying it.

## Evidence classes and sources

Official IEEE Author Center pages, checked 2026-10-26:

- [Resolution and Size](https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-graphics-for-your-article/resolution-and-size/): typical widths are 88.9 mm (one column) and 182 mm (two columns); accepted vector formats include PS/EPS/PDF. Its raster guidance distinguishes color/grayscale (>300 dpi) from black-and-white line art (>600 dpi). A chat preview PNG is not automatically a publication raster.
- [File Formatting](https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-graphics-for-your-article/file-formatting/): embed fonts or convert text to outlines in vector files; use consistent typography with approximately 9–10 pt lettering at final size. This is approximate guidance, not a universal minimum for every secondary annotation. Its file-preparation guidance lists 182 × 220 mm as maximum graphic dimensions.
- [Create Graphics](https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-graphics-for-your-article/): check grayscale interpretation and use redundant visual encodings. No black-and-white-only requirement or official TWC palette is established by these sources. Check current [TWC policies](https://www.comsoc.org/publications/journals/ieee-twc/policies-guidelines) for the actual submission context.

Observed precedents, inspected as actual figure images rather than inferred from abstracts:

| Paper and locator | Useful design observation | Boundary |
| --- | --- | --- |
| Wu et al., *Deep Joint Source-Channel Coding for Adaptive Image Transmission over MIMO Channels*, TWC, DOI 10.1109/TWC.2024.3422794; [author PDF](https://arxiv.org/pdf/2309.00470), Fig.3, PDF p.6 | Opposing encoder/decoder reading directions can form a coherent architecture. Compact layer bars and a nearby local expansion separate overview from detail. | An author version is not proof of final publisher artwork; its palette and exact composition are not mandatory. |
| Guo et al., *Diffusion-Driven Semantic Communication for Generative Models With Bandwidth Constraints*, TWC, DOI 10.1109/TWC.2025.3553851; [author PDF](https://arxiv.org/pdf/2407.18468), Fig.2, PDF p.4 | Grouped processes, compact data glyphs and clearly distinguished main/auxiliary paths make communication-and-learning relations easier to trace. | Do not copy the artwork or transfer its diffusion/channel equivalence claims to an unrelated method. |

Public viewing is not artwork reuse permission. Keep these as observation-only references; do not bundle their images, private manuscript figures or client labels in the plugin.

## Decisions that improve model figures

1. **Compose for the actual page width.** Estimate final height as well as font size before polishing. Compare information density across panels. A tall local block beside a short overview can create large diagonal blank regions; rebalance placement or local spacing within the approved layout. Do not fill every blank region or impose a fixed aspect ratio. Never compress arrows until labels or marker landing space become crowded.
2. **Give the main computation a continuous reading path.** A U-shaped encoder/decoder is legitimate. Inspect where a reader must reverse direction or hunt for the next arrow, rather than treating all upward arrows as errors. Put ordinary operations on short paths and keep explanatory detail secondary.
3. **Place conditioning near its consumer when possible.** First try moving the condition node and choosing a better attachment face before routing around a page or a different panel. Distinguish positional inputs, timestep inputs, residuals and parameter transfer in their actual roles. Do not create a bus, junction, dependency or change of line meaning simply to shorten a line.
4. **Explain bundled channels without proliferating lines.** Four connections can legitimately carry six parameter vectors when two connections carry scale/shift pairs and two carry gates. Make this grouping explicit with short labels or a compact figure-internal legend tied to the relevant local block. Do not infer a missing edge from the line count alone, or draw six crowded long paths when the approved graph bundles pairs.
5. **Mark explanatory insets as explanations.** A patch-to-token inset can look like a detached computational branch if it has a calculation arrow but no connection back to the model. Identify it as a detail and state which operation it illustrates. Do not add a scientific edge just to remove the visual ambiguity. Keep schematic data glyphs visibly distinct from measured predictions, with their status in the caption.
6. **Use hierarchy and restrained styling.** Differentiate panel headings, operation labels and auxiliary notes; align tensor-size annotations with the object they describe and keep transfer labels close to their arrows. Color is optional. If used, pair it with shapes, labels or line styles. Flat white/black or restrained color can both work; neither establishes journal fit by itself.

## Review routes and arrows separately

Read [connector-reliability.md](connector-reliability.md) for endpoint and route planning. A zero-crossing graph and a passing arrowhead helper are insufficient for visual approval.

- **Scientific correctness:** trace every source–relation–target; verify addition/multiplication order, residual tap location, conditioning inputs and parameter-transfer scope. A fork after a sum must not be drawn as if it came from the residual input. Check model code or the approved method contract when needed.
- **Geometric correctness:** inspect actual text ink, target ports, marker direction, straight landing space, unrelated objects and unintended intersections/overlaps in the exported artifact. Review native-source/export parity separately.
- **Human readability:** follow complete paths at intended size. Check detours, short initial doglegs as well as final legs, proximity to panel borders, ownership of labels and confusion between neighboring panels. Compare feasible routes for length and bends without claiming a mathematical optimum. A route's Manhattan-distance ratio alone ignores obstacles and cannot certify quality.
- **Delivery quality:** inspect the actual PDF/PNG selected by the delivery contract, embedded fonts and final-size typography. Preserve the editable source. Keep schema validation, arrow-helper results, visual judgment, author acceptance and publisher compliance as distinct evidence.

Report findings with locations and classify them as a connection/meaning error, a readability/layout issue, or an aesthetic preference. Do not manufacture hard errors from an untidy but correctly connected path. Keep unverified renderer or manuscript-placement checks visible. Numeric clearances used by a particular figure remain local QA heuristics; do not present them as TWC rules or universal plugin thresholds.
