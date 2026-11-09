"""Deterministic ZIP policy shared by project packaging CLIs only."""
from __future__ import annotations

import hashlib
import os
import tempfile
import zipfile
from pathlib import Path

FIXED_TIMESTAMP = (2026, 1, 1, 0, 0, 0)


def package_files(skill_root: Path) -> list[Path]:
    files = []
    for path in skill_root.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"refusing to package symlink: {path}")
        if not path.is_file():
            continue
        if path.name == ".gitignore" or "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        files.append(path)
    return sorted(files, key=lambda path: path.relative_to(skill_root).as_posix())


def archive_permissions(source: Path) -> int:
    """Preserve executability, not host-specific owner/group write permissions."""
    return (0o755 if source.stat().st_mode & 0o111 else 0o644) << 16


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_archive(name: str, version: str, source_root: Path, output_dir: Path) -> dict[str, object]:
    destination = output_dir / f"{name}-{version}.zip"
    files = package_files(source_root)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=output_dir
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        with zipfile.ZipFile(
            temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
        ) as archive:
            for source in files:
                relative = source.relative_to(source_root)
                info = zipfile.ZipInfo(
                    f"{name}/{relative.as_posix()}", FIXED_TIMESTAMP
                )
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = archive_permissions(source)
                archive.writestr(info, source.read_bytes())
        os.replace(temporary, destination)
        destination.chmod(0o644)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass
    return {
        "path": str(destination),
        "files": len(files),
        "sha256": sha256(destination),
    }
