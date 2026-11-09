#!/usr/bin/env python3
"""Build deterministic install-ready ZIPs for the configured runtime skills."""

from __future__ import annotations

import argparse
import json
import tomllib
from pathlib import Path

from archive_utils import build_archive
from project_config import SkillConfig, load_project

ROOT = Path(__file__).resolve().parents[1]


def project_metadata() -> tuple[str, list[SkillConfig]]:
    project, _, skills = load_project(ROOT)
    return project["version"], skills


def build_package(config: SkillConfig, output_dir: Path) -> dict[str, object]:
    return {"skill": config.name, "kind": config.kind, "version": config.version,
            **build_archive(config.name, config.version, config.path, output_dir)}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Package configured runtime skills.")
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--all", action="store_true", help="package every configured skill")
    selection.add_argument(
        "--skill", action="append", metavar="NAME", help="package one named skill"
    )
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist")
    parser.add_argument("--force", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        project_version, configured = project_metadata()
        by_name = {skill.name: skill for skill in configured}
        if len(by_name) != len(configured):
            raise ValueError("configured skill names must be unique")
        if args.all:
            selected = configured
        else:
            unknown = sorted(set(args.skill) - set(by_name))
            if unknown:
                raise ValueError(f"unknown skill names: {unknown}")
            selected = [by_name[name] for name in args.skill]

        output_dir = args.output_dir.expanduser().resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        destinations = [output_dir / f"{item.name}-{item.version}.zip" for item in selected]
        existing = [str(path) for path in destinations if path.exists()]
        if existing and not args.force:
            raise ValueError(f"refusing to overwrite existing packages: {existing}")

        packages = [build_package(item, output_dir) for item in selected]
        print(
            json.dumps(
                {
                    "status": "written",
                    "project_version": project_version,
                    "packages": packages,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    except (KeyError, OSError, TypeError, ValueError, tomllib.TOMLDecodeError) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
