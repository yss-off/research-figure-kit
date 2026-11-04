# Poster review and text tools

## Diagnose the rejected result

| Symptom | Inspect before changing style |
| --- | --- |
| Many boxes feel clumsy | Too many container roles? Excessive height/padding? Repeated condition text? |
| No boxes feels empty | Weak grouping, faint connectors, uniform weight, or overly distant related labels? |
| Notes dominate | Their area, heading size and color compete with the actual decision/action? |
| Logo feels tiny or pasted on | Relative scale at viewing size, preserved aspect, clear space and raster background? |
| Prices fit at full resolution only | Three columns plus inline labels may not fit mobile width; increase space or relax that arrangement instead of silently shrinking the text. |
| A short line leaves large blank space | Old manual newline, a text box narrower than the note region, or an unnecessarily separate paragraph? |
| Repeated copy corrections | Did the latest accepted meaning actually reach the canonical source and every related label? |

Do not prescribe one house style from a single poster. Rounded versus unboxed nodes, centered versus left-aligned titles, and horizontal versus vertical outcomes depend on the content and the user's settled preference. Typography can be simplified to a small set of roles without forcing exactly three font sizes.

## Viewing-size audit

```bash
python scripts/poster_tools.py audit poster.drawio \
  --source-width 960 --display-width 432 \
  --primary-ids 3,8,12 --secondary-ids 20,21
```

Resolve IDs from the current exported XML, not stale source IDs. The source width is in the same coordinate scale as Draw.io geometry (typically the exported SVG viewBox width); for a raster rendered at 3× scale, use raster width / 3. Never use the 300dpi metadata as the viewing-size scale.

The default review thresholds are 14px for primary content and 10px for secondary content. These are adjustable triage values, not accessibility certification or a legibility guarantee. The tool returns `review` (exit 1) for small text, unclassified visible labels or missing font sizes, `clear` (exit 0) only for those checks, and exit 2 for invalid inputs. It reads one uncompressed page; it rejects compressed or multiple-page inputs rather than silently auditing the wrong page. It does not inspect arrows, images, visible glyphs or aesthetic quality.

A 24px label on a 1280-unit poster becomes only 8.1px at 432px. A technically valid high-resolution PNG can still be a poor chat poster. Audit the display target before claiming readiness, then inspect the real export.

## Measured wrapping

```bash
python scripts/poster_tools.py wrap note.txt \
  --font /absolute/path/to/cjk-font.otf --font-size 22 --width 800 \
  --keep '备用选择' --keep '我们'
```

Pillow is an optional local dependency for this command; the audit command uses only the standard library. Do not install dependencies silently during a drawing task. Use an installed font matching the renderer; font fallback or a different font weight invalidates the measurement. Output includes measured line widths, the font hash, and the original text. Explicit paragraphs are preserved by default; `--collapse-newlines` is for an authorized conversion to one paragraph. Latin identifiers/numbers and protected phrases are not split. Unbreakable tokens wider than the box are errors, not silently overflowed or reduced in size.

This helper cannot infer every Chinese word boundary. Inspect line beginnings/endings, protect meaningful phrases where needed, and distinguish measured width from actual rendered appearance. No extra spaces or justified spacing should be inserted merely to fill a short final line.

## Revision receipt

A compact work-directory record is enough; extend only when useful:

```json
{
  "source": "poster.spec.yaml",
  "change": "One outcome label and one explanatory note",
  "content_checked": ["branch conditions unchanged", "units preserved"],
  "display_width": 432,
  "export": "poster.preview.png",
  "geometry": "checked",
  "visual_findings": ["No clipped note; primary labels readable at target size"],
  "unresolved": ["Service duration not supplied"],
  "user_acceptance": "not_requested"
}
```

Report evidence honestly. Do not turn a blank `unresolved` list into a claim that an offer, external channel or official policy has been independently verified.
