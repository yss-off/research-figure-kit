#!/usr/bin/env python3
"""Build a deterministic install-ready ZIP for the configured Codex plugin."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
import tomllib
import zipfile
from pathlib import Path

from package_skill import FIXED_TIMESTAMP, archive_permissions, package_files, sha256

ROOT = Path(__file__).resolve().parents[1]


def plugin_metadata() -> tuple[str, str, Path]:
    with (ROOT / "pyproject.toml").open("rb") as handle:
        document = tomllib.load(handle)
    project_version = document["project"]["version"]
    record = document["tool"]["academic_figure_skills"]["plugin"]
    name = record["name"]
    version = record["version"]
    path = (ROOT / record["path"]).resolve()
    path.relative_to(ROOT)
    if project_version != version:
        raise ValueError("plugin version must match project.version")

    manifest = json.loads(
        (path / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
    )
    if manifest.get("name") != name or manifest.get("version") != version:
        raise ValueError("plugin manifest name/version does not match pyproject.toml")
    return name, version, path


def build_plugin(name: str, version: str, plugin_root: Path, output_dir: Path) -> dict[str, object]:
    destination = output_dir / f"{name}-{version}.zip"
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=output_dir
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    files = package_files(plugin_root)
    try:
        with zipfile.ZipFile(
            temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
        ) as archive:
            for source in files:
                relative = source.relative_to(plugin_root)
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
        "plugin": name,
        "version": version,
        "path": str(destination),
        "files": len(files),
        "sha256": sha256(destination),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Package the configured Codex plugin.")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist")
    parser.add_argument("--force", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        name, version, plugin_root = plugin_metadata()
        output_dir = args.output_dir.expanduser().resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        destination = output_dir / f"{name}-{version}.zip"
        if destination.exists() and not args.force:
            raise ValueError(f"refusing to overwrite existing package: {destination}")
        package = build_plugin(name, version, plugin_root, output_dir)
        print(json.dumps({"status": "written", "package": package}, indent=2, sort_keys=True))
        return 0
    except (KeyError, OSError, TypeError, ValueError, tomllib.TOMLDecodeError) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
