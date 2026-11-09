"""Read the single project manifest for verification and both package entrypoints."""
from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


class ProjectConfigError(ValueError):
    """Invalid project metadata, reported by the calling CLI."""


@dataclass(frozen=True)
class SkillConfig:
    name: str
    version: str
    path: Path
    kind: str
    base_skill_name: str | None = None
    source_url: str | None = None
    source_commit: str | None = None


@dataclass(frozen=True)
class PluginConfig:
    name: str
    version: str
    path: Path
    marketplace_path: Path


def resolve_project_path(root: Path, relative_path: str, field: str) -> Path:
    if not isinstance(relative_path, str) or not relative_path:
        raise ProjectConfigError(f"{field} must be a non-empty string")
    path = (root / relative_path).resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise ProjectConfigError(f"{field} must stay inside the project: {path}") from exc
    return path


def load_project(root: Path = ROOT) -> tuple[dict[str, Any], PluginConfig, list[SkillConfig]]:
    root = root.resolve()
    with (root / "pyproject.toml").open("rb") as handle:
        document = tomllib.load(handle)
    project = document.get("project")
    tool = document.get("tool")
    settings = tool.get("academic_figure_skills") if isinstance(tool, dict) else None
    if not isinstance(project, dict) or not isinstance(settings, dict):
        raise ProjectConfigError("pyproject.toml is missing project/tool metadata")
    if not isinstance(project.get("version"), str) or not project["version"]:
        raise ProjectConfigError("project.version must be a non-empty string")
    plugin_record = settings.get("plugin")
    if not isinstance(plugin_record, dict):
        raise ProjectConfigError("tool.academic_figure_skills.plugin must be a table")
    try:
        plugin = PluginConfig(
            name=plugin_record["name"],
            version=plugin_record["version"],
            path=resolve_project_path(root, plugin_record["path"], "plugin.path"),
            marketplace_path=resolve_project_path(
                root, plugin_record["marketplace_path"], "plugin.marketplace_path"
            ),
        )
    except KeyError as exc:
        raise ProjectConfigError(f"plugin metadata is missing {exc.args[0]}") from exc
    if not all(isinstance(value, str) and value for value in (plugin.name, plugin.version)):
        raise ProjectConfigError("plugin name and version must be non-empty strings")
    records = settings.get("skills")
    if not isinstance(records, list) or not records:
        raise ProjectConfigError("tool.academic_figure_skills.skills must be a non-empty list")

    skills: list[SkillConfig] = []
    for record in records:
        if not isinstance(record, dict):
            raise ProjectConfigError("every configured skill must be a table")
        try:
            name = record["name"]
            version = record["version"]
            kind = record["kind"]
            relative_path = record["path"]
        except KeyError as exc:
            raise ProjectConfigError(f"configured skill is missing {exc.args[0]}") from exc
        if not all(isinstance(value, str) and value for value in (name, version, kind, relative_path)):
            raise ProjectConfigError("skill name, version, kind, and path must be non-empty strings")
        path = resolve_project_path(root, relative_path, "skill.path")
        base_name = record.get("base_skill_name")
        if base_name is not None and not isinstance(base_name, str):
            raise ProjectConfigError("base_skill_name must be a string when present")
        source_url = record.get("source_url")
        source_commit = record.get("source_commit")
        if source_url is not None and not isinstance(source_url, str):
            raise ProjectConfigError("source_url must be a string when present")
        if source_commit is not None and not isinstance(source_commit, str):
            raise ProjectConfigError("source_commit must be a string when present")
        skills.append(
            SkillConfig(
                name,
                version,
                path,
                kind,
                base_name,
                source_url,
                source_commit,
            )
        )

    if len({skill.name for skill in skills}) != len(skills):
        raise ProjectConfigError("configured skill names must be unique")
    if len({skill.path for skill in skills}) != len(skills):
        raise ProjectConfigError("configured skill paths must be unique")
    return project, plugin, skills
