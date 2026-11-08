"""Explicit bilingual serif fonts; no silent substitute or bundled font files."""
from pathlib import Path


def bilingual_serif_style(*, font_paths=(), text=""):
    """Register supplied local fonts, validate coverage, return scoped rcParams.

    Latin/digits resolve to Times New Roman first; CJK resolves to SimSun.
    Call before creating artists and use the returned dict in mpl.rc_context.
    Fonts must be supplied by the caller or installed locally, never downloaded.
    """
    from matplotlib import font_manager, ft2font
    for path in font_paths:
        font_manager.fontManager.addfont(str(Path(path)))
    families = ["Times New Roman", "SimSun"]
    paths = []
    maps = []
    for family in families:
        try:
            path = font_manager.findfont(
                font_manager.FontProperties(family=[family]), fallback_to_default=False)
        except ValueError as exc:
            raise ValueError(f"Required font {family!r} is missing; supply a licensed local font file.") from exc
        face = ft2font.FT2Font(path)
        if face.family_name != family:
            raise ValueError(f"Expected {family!r}, resolved {face.family_name!r}")
        paths.append(path)
        maps.append(face.get_charmap())
    missing = sorted({c for c in text if not c.isspace() and not any(ord(c) in m for m in maps)})
    if missing:
        raise ValueError(f"Required fonts cannot render these characters: {''.join(missing)}")
    return {
        "font.family": families,
        "axes.unicode_minus": True,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "path",
        "text.usetex": False,
    }, {"families": families, "files": paths,
        "svg_text": "outlined for portable rendering; keep plotting source for editing"}
