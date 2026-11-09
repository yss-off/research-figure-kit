#!/usr/bin/env python3
"""Build a deterministic install-ready ZIP for the configured Codex plugin."""

from __future__ import annotations

import argparse
import json
import tomllib
from pathlib import Path

from archive_utils import build_archive
from project_config import load_project

ROOT = Path(__file__).resolve().parents[1]


def plugin_metadata() -> tuple[str, str, Path]:
    project, plugin, _ = load_project(ROOT)
    project_version = project["version"]
    name, version, path = plugin.name, plugin.version, plugin.path
    if project_version != version:
        raise ValueError("plugin version must match project.version")

    manifest = json.loads(
        (path / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
    )
    if manifest.get("name") != name or manifest.get("version") != version:
        raise ValueError("plugin manifest name/version does not match pyproject.toml")
    return name, version, path


def build_plugin(name: str, version: str, plugin_root: Path, output_dir: Path) -> dict[str, object]:
    return {"plugin": name, "version": version,
            **build_archive(name, version, plugin_root, output_dir)}


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
