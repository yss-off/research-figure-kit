# Connector routing feedback — 2026-10-26

User asked for research-based routing repair and local plugin feedback. Source
repo changes only; no base renderer/cache/install/release modifications.

## Finding
Earlier guidance concentrated on arrowhead landing space. A path with no
crossings can still make an adjacent cross-panel relation detour around a page.
The previous helper does not assess that. Fix authoring policy in the overlay.

## Change
Expanded connector-reliability.md with a route ledger and the order: preserve
semantics → allocate ports/corridors → avoid objects and ambiguous joins →
compare bends/length → place labels → inspect exported paths. SKILL.md points
to route-level review and explicitly bounds the helper's claim. Research links
and access limitations live in the runtime reference. No client content or
figure is copied into the plugin.

## Validation
Documentation-only change: inspect diff, referenced local paths, and source
preservation. No new runtime code; no automatic-router performance claimed.
Representative exported figure is reviewed in its own project work directory.
User visual acceptance and native Desktop/Word parity remain unresolved.
