#!/usr/bin/env python3
"""Build deterministic install-ready ZIPs for the configured runtime skills."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
import tomllib
import zipfile
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXED_TIMESTAMP = (2026, 1, 1, 0, 0, 0)


@dataclass(frozen=True)
class SkillConfig:
    name: str
    version: str
    path: Path
    kind: str


def project_metadata() -> tuple[str, list[SkillConfig]]:
    with (ROOT / "pyproject.toml").open("rb") as handle:
        document = tomllib.load(handle)
    project_version = document["project"]["version"]
    records = document["tool"]["academic_figure_skills"]["skills"]
    skills: list[SkillConfig] = []
    for record in records:
        path = (ROOT / record["path"]).resolve()
        path.relative_to(ROOT)
        skills.append(
            SkillConfig(
                name=record["name"],
                version=record["version"],
                path=path,
                kind=record["kind"],
            )
        )
    return project_version, skills


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


def build_package(config: SkillConfig, output_dir: Path) -> dict[str, object]:
    destination = output_dir / f"{config.name}-{config.version}.zip"
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=output_dir
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    files = package_files(config.path)
    try:
        with zipfile.ZipFile(
            temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
        ) as archive:
            for source in files:
                relative = source.relative_to(config.path)
                info = zipfile.ZipInfo(
                    f"{config.name}/{relative.as_posix()}", FIXED_TIMESTAMP
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
        "skill": config.name,
        "kind": config.kind,
        "version": config.version,
        "path": str(destination),
        "files": len(files),
        "sha256": sha256(destination),
    }


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
