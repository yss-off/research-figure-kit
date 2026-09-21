<div align="center">

# Research Figure Kit

**Research figures you can edit, check, and reproduce.**

[![CI](https://github.com/yss-off/research-figure-kit/actions/workflows/ci.yml/badge.svg)](https://github.com/yss-off/research-figure-kit/actions/workflows/ci.yml)
[![Version](https://img.shields.io/badge/version-0.3.4-2563EB)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/license-MIT-0B7285)](LICENSE)
[![Codex Plugin](https://img.shields.io/badge/Codex-plugin-111827)](plugins/academic-figure-skills/.codex-plugin/plugin.json)

[中文说明](README_CN.md)

<img src="assets/social/research-figure-kit-x-launch.png" alt="Research Figure Kit turns structured figure sources into editable diagrams, scientific plots, and validation evidence." width="100%">

</div>

AI can generate a research figure quickly. Making it **editable**, **verifiable**, and **reproducible** is harder.

Research Figure Kit is an open-source Codex plugin that treats a figure as an evidence-bearing artifact rather than a disposable image. It combines structured Draw.io authoring, publication-aware diagram review, and evidence-aware scientific visualization in one installable plugin—while keeping their rendering backends separate.

## What ships in the plugin

| Skill | Best for | Canonical source | Evidence and output |
|---|---|---|---|
| `drawio` | General diagrams, architecture, network topology, UML, flowcharts, and `.drawio` editing | YAML | Editable `.drawio`, SVG/PNG, validation diagnostics |
| `drawio-academic-skills` | Paper, thesis, manuscript, and Word-facing architecture, mechanism, workflow, and roadmap figures | YAML + figure manifest | Layout alternatives, semantic gates, editable source, publication artifact |
| `drawio-poster` | Branded service-flow posters, customer decision guides, mobile review and concise notes | YAML + revision evidence | Editable poster, viewing-size audit, measured text wrapping |
| `scientific-visualization` | Numeric data, uncertainty, repeated units, missingness, statistical encoding, Matplotlib/Seaborn/Plotly | Data + plotting code + figure contract | Read-only profile, chart rationale, plot, export and QA evidence |

## Why it is different

- **Editable by default** — Draw.io workflows retain the `.drawio` source instead of flattening the result into an opaque image.
- **Semantics before polish** — complex figures can freeze nodes, arrows, prohibited edges, forbidden interpretations, and cross-cutting regions before detailed layout.
- **Evidence instead of vibes** — manifests record sources, renderers, hashes, QA status, and residual risks; missing evidence is never silently promoted to `PASS`.
- **Publication-aware delivery** — choose one explicit contract: `raster-publication`, `vector-submission`, or `draft-preview`.
- **Honest scientific plotting** — the data workflow profiles inputs without silently cleaning, imputing, merging, or choosing a statistical test.
- **Offline-first core** — normal authoring, validation, and packaging do not require a live backend.

## Install

```bash
git clone https://github.com/yss-off/research-figure-kit.git
cd research-figure-kit
codex plugin marketplace add .
codex plugin add academic-figure-skills@research-figure-kit
```

Verify that the plugin is visible:

```bash
codex plugin list --json --available
```

The optional live Draw.io backend in `drawio/.mcp.json` is not required by the offline workflow. If used, `npx` downloads its pinned package version.

## Try it

### Publication diagram

```text
Use drawio-academic-skills to turn this method description into an editable
paper workflow. Compare layout plans before rendering and keep the scientific
relationships unchanged during visual cleanup.
```

### Scientific plot

```text
Use scientific-visualization to inspect results.csv read-only, identify the
repeated unit and uncertainty structure, and recommend a truthful figure before
writing plotting code.
```

### Existing Draw.io file

```text
Edit this .drawio file. Preserve the node and edge inventory, fix ambiguous
arrows and title spacing, then validate the final artifact at Word page scale.
```

## Quality gates

The project separates four kinds of evidence:

1. **Structural** — schema, stable IDs, graph relations, artifact integrity.
2. **Semantic** — claims, non-edges, prohibited interpretations, loop meaning.
3. **Visual** — overlap, clipping, spacing, label ownership, font fallback.
4. **Publication** — target width, effective resolution, document embedding, venue constraints.

A green structural validator does not automatically prove that a figure is scientifically correct or visually publication-ready.

## Development

The plugin source lives under `plugins/academic-figure-skills/`. Project governance and historical validation records stay outside the runtime package.

```bash
python -m pip install -r requirements-dev.txt
make test
make test-routing
make check
make check-base
make check-plugin   # requires the Codex plugin-creator system skill
make package
```

GitHub Actions runs the portable test, routing, project, base-compatibility, and deterministic-package checks. The generated plugin ZIP is attached to each successful CI run as an artifact.

## Repository map

```text
.
├── .agents/plugins/marketplace.json
├── plugins/academic-figure-skills/
│   ├── .codex-plugin/plugin.json
│   ├── THIRD_PARTY_NOTICES.md
│   └── skills/
│       ├── drawio/
│       ├── drawio-academic-skills/
│       ├── drawio-poster/
│       └── scientific-visualization/
├── evals/                 # cross-skill routing cases
├── management/            # provenance and engineering decisions
├── tools/                 # verification and deterministic packaging
├── tests/                 # repository-level test entry point
└── Makefile
```

## Contributing and security

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) and the [Code of Conduct](CODE_OF_CONDUCT.md). Report vulnerabilities through the private channel described in [SECURITY.md](SECURITY.md), not through a public issue.

## License and attribution

Research Figure Kit is released under the [MIT License](LICENSE).

The bundled `drawio` base is fixed to [`bahayonghang/drawio-skills@27dac02`](https://github.com/bahayonghang/drawio-skills/commit/27dac02ce3b4901c844aaa623ad64c3d577c3a72). The scientific-visualization skill adapts work from K-Dense AI's `scientific-agent-skills`. Full notices and embedded third-party licenses are recorded in [THIRD_PARTY_NOTICES.md](plugins/academic-figure-skills/THIRD_PARTY_NOTICES.md).
