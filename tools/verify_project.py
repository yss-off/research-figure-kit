#!/usr/bin/env python3
"""Offline verifier for the unified academic figure skills project."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"


class VerificationError(RuntimeError):
    """Raised when a project invariant or subprocess check fails."""


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


def run_checked(command: list[str], *, env: dict[str, str] | None = None) -> str:
    result = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    output = "\n".join(part for part in (result.stdout, result.stderr) if part).strip()
    if result.returncode != 0:
        raise VerificationError(
            f"command failed ({result.returncode}): {' '.join(command)}\n{output}"
        )
    return output


def resolve_project_path(relative_path: str, field: str) -> Path:
    path = (ROOT / relative_path).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise VerificationError(f"{field} must stay inside the project: {path}") from exc
    return path


def load_project() -> tuple[dict[str, Any], PluginConfig, list[SkillConfig]]:
    with PYPROJECT.open("rb") as handle:
        document = tomllib.load(handle)
    project = document.get("project")
    settings = document.get("tool", {}).get("academic_figure_skills")
    if not isinstance(project, dict) or not isinstance(settings, dict):
        raise VerificationError("pyproject.toml is missing project/tool metadata")
    if not isinstance(project.get("version"), str) or not project["version"]:
        raise VerificationError("project.version must be a non-empty string")
    plugin_record = settings.get("plugin")
    if not isinstance(plugin_record, dict):
        raise VerificationError("tool.academic_figure_skills.plugin must be a table")
    try:
        plugin = PluginConfig(
            name=plugin_record["name"],
            version=plugin_record["version"],
            path=resolve_project_path(plugin_record["path"], "plugin.path"),
            marketplace_path=resolve_project_path(
                plugin_record["marketplace_path"], "plugin.marketplace_path"
            ),
        )
    except KeyError as exc:
        raise VerificationError(f"plugin metadata is missing {exc.args[0]}") from exc
    if not all(isinstance(value, str) and value for value in (plugin.name, plugin.version)):
        raise VerificationError("plugin name and version must be non-empty strings")
    records = settings.get("skills")
    if not isinstance(records, list) or not records:
        raise VerificationError("tool.academic_figure_skills.skills must be a non-empty list")

    skills: list[SkillConfig] = []
    for record in records:
        if not isinstance(record, dict):
            raise VerificationError("every configured skill must be a table")
        try:
            name = record["name"]
            version = record["version"]
            kind = record["kind"]
            relative_path = record["path"]
        except KeyError as exc:
            raise VerificationError(f"configured skill is missing {exc.args[0]}") from exc
        if not all(isinstance(value, str) and value for value in (name, version, kind, relative_path)):
            raise VerificationError("skill name, version, kind, and path must be non-empty strings")
        path = resolve_project_path(relative_path, "skill.path")
        base_name = record.get("base_skill_name")
        if base_name is not None and not isinstance(base_name, str):
            raise VerificationError("base_skill_name must be a string when present")
        source_url = record.get("source_url")
        source_commit = record.get("source_commit")
        if source_url is not None and not isinstance(source_url, str):
            raise VerificationError("source_url must be a string when present")
        if source_commit is not None and not isinstance(source_commit, str):
            raise VerificationError("source_commit must be a string when present")
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
        raise VerificationError("configured skill names must be unique")
    if len({skill.path for skill in skills}) != len(skills):
        raise VerificationError("configured skill paths must be unique")
    return project, plugin, skills


def frontmatter_text(skill_root: Path) -> str:
    text = (skill_root / "SKILL.md").read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise VerificationError(f"{skill_root.name}/SKILL.md is missing frontmatter")
    try:
        return text.split("---\n", 2)[1]
    except IndexError as exc:
        raise VerificationError(f"{skill_root.name}/SKILL.md has invalid frontmatter") from exc


def frontmatter_field(skill_root: Path, field: str) -> str | None:
    pattern = re.compile(
        rf"^\s*{re.escape(field)}:\s*[\"']?([^\"'\n]+)[\"']?\s*$",
        re.MULTILINE,
    )
    match = pattern.search(frontmatter_text(skill_root))
    return match.group(1).strip() if match else None


def packaged_runtime_files(skill_root: Path) -> list[Path]:
    files: list[Path] = []
    for path in skill_root.rglob("*"):
        if path.is_file() and path.name != ".gitignore" and "__pycache__" not in path.parts and path.suffix != ".pyc":
            files.append(path)
    return files


def required_files(config: SkillConfig) -> tuple[Path, ...]:
    if config.kind == "drawio-base":
        return (
            config.path / "SKILL.md",
            config.path / "agents" / "openai.yaml",
            config.path / "assets" / "schemas" / "spec.schema.json",
            config.path / "scripts" / "cli.js",
            config.path / "scripts" / "vendor" / "js-yaml" / "LICENSE.md",
            config.path / "scripts" / "vendor" / "elkjs" / "LICENSE.md",
        )
    common = (config.path / "SKILL.md", config.path / "evals" / "smoke_test.py")
    if config.kind == "drawio-overlay":
        return common + (
            config.path / "agents" / "openai.yaml",
            config.path / "assets" / "schemas" / "figure-manifest.schema.json",
            config.path / "evals" / "evals.json",
            config.path / "scripts" / "figure_manifest.py",
        )
    if config.kind == "poster-overlay":
        return common + (
            config.path / "agents" / "openai.yaml",
            config.path / "references" / "poster-review.md",
            config.path / "scripts" / "poster_tools.py",
        )
    if config.kind == "scientific-plotting":
        return common + (
            config.path / "assets" / "publisher_profiles.json",
            config.path / "evals" / "trigger_cases.json",
            config.path / "references" / "figure_contract.md",
            config.path / "scripts" / "figure_export.py",
            config.path / "scripts" / "profile_data.py",
            config.path / "scripts" / "visual_qa.py",
        )
    raise VerificationError(f"unsupported skill kind: {config.kind}")


def validate_skill_structure(config: SkillConfig) -> dict[str, object]:
    missing = [str(path.relative_to(ROOT)) for path in required_files(config) if not path.is_file()]
    if missing:
        raise VerificationError(f"required skill files are missing: {missing}")

    forbidden_runtime_docs = ("README.md", "README_CN.md", "CHANGELOG.md")
    present = [name for name in forbidden_runtime_docs if (config.path / name).exists()]
    if present:
        raise VerificationError(f"project-only documents in {config.name}: {present}")

    symlinks = [str(path.relative_to(ROOT)) for path in config.path.rglob("*") if path.is_symlink()]
    if symlinks:
        raise VerificationError(f"runtime skill must not contain symlinks: {symlinks}")

    declared_name = frontmatter_field(config.path, "name")
    if declared_name != config.name:
        raise VerificationError(
            f"{config.name} frontmatter name mismatch: {declared_name!r}"
        )
    if config.kind == "drawio-overlay":
        evals = json.loads((config.path / "evals" / "evals.json").read_text(encoding="utf-8"))
        if evals.get("version") != config.version:
            raise VerificationError(
                f"{config.name} eval version must match configured version {config.version}"
            )
    elif config.kind in {"drawio-base", "scientific-plotting", "poster-overlay"}:
        declared_version = frontmatter_field(config.path, "version")
        if declared_version != config.version:
            raise VerificationError(
                f"{config.name} frontmatter version must match configured version {config.version}"
            )
    else:
        raise VerificationError(f"unsupported skill kind: {config.kind}")

    if config.kind == "drawio-base":
        if not config.source_url or not config.source_commit:
            raise VerificationError("drawio-base requires source_url and source_commit")
        provenance = {
            "upstream": (config.source_url, frontmatter_field(config.path, "upstream")),
            "upstream_commit": (
                config.source_commit,
                frontmatter_field(config.path, "upstream_commit"),
            ),
        }
        mismatches = {
            field: {"expected": expected, "actual": actual}
            for field, (expected, actual) in provenance.items()
            if expected != actual
        }
        if mismatches:
            raise VerificationError(f"drawio-base provenance mismatch: {mismatches}")

    json_files = sorted(config.path.rglob("*.json"))
    for path in json_files:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise VerificationError(f"invalid JSON: {path.relative_to(ROOT)}: {exc}") from exc

    skill_lines = len((config.path / "SKILL.md").read_text(encoding="utf-8").splitlines())
    if skill_lines > 500:
        raise VerificationError(f"{config.name}/SKILL.md exceeds 500 lines: {skill_lines}")
    return {
        "kind": config.kind,
        "version": config.version,
        "runtime_files": len(packaged_runtime_files(config.path)),
        "json_files": len(json_files),
        "skill_lines": skill_lines,
    }


def find_quick_validator(explicit: Path | None) -> Path | None:
    candidates = [
        explicit,
        Path.home() / ".codex" / "skills" / ".system" / "skill-creator" / "scripts" / "quick_validate.py",
    ]
    return next((path for path in candidates if path and path.is_file()), None)


def validation_environment(cache_root: Path) -> dict[str, str]:
    environment = dict(os.environ)
    environment["PYTHONPYCACHEPREFIX"] = str(cache_root / "pycache")
    environment["MPLCONFIGDIR"] = str(cache_root / "matplotlib")
    return environment


def validate_skill_runtime(
    config: SkillConfig, validator: Path | None, cache_root: Path
) -> dict[str, object]:
    environment = validation_environment(cache_root)
    result: dict[str, object] = {}
    if config.kind == "drawio-base":
        run_checked(["node", str(config.path / "scripts" / "cli.js"), "--help"], env=environment)
        result["cli_help"] = "pass"
    else:
        run_checked(
            [sys.executable, str(config.path / "evals" / "smoke_test.py")],
            env=environment,
        )
        result["smoke_tests"] = "pass"
    if validator:
        run_checked([sys.executable, str(validator), str(config.path)], env=environment)
        result["skill_validation"] = "pass"
    else:
        result["skill_validation"] = "not_available"

    if config.kind == "scientific-plotting":
        helpers = sorted(
            path for path in (config.path / "scripts").glob("*.py") if path.name != "_common.py"
        )
        for helper in helpers:
            run_checked([sys.executable, str(helper), "--help"], env=environment)
        result["cli_help"] = {"status": "pass", "scripts": len(helpers)}
    return result


def find_base(explicit: Path | None, bundled: Path) -> Path:
    candidates = [
        explicit,
        bundled,
        Path.home() / ".codex" / "skills" / "drawio",
        Path.home() / ".agents" / "skills" / "drawio",
    ]
    for candidate in candidates:
        if candidate and (candidate / "scripts" / "cli.js").is_file():
            return candidate.resolve()
    raise VerificationError("sibling base not found; pass --base /path/to/drawio")


def validate_base(skill_root: Path, base_root: Path) -> dict[str, Any]:
    sources = sorted((skill_root / "references" / "examples").glob("*.yaml"))
    sources += sorted((skill_root / "references" / "templates").glob("*.yaml"))
    notices: set[str] = set()
    with tempfile.TemporaryDirectory(prefix="drawio-academic-base-") as temporary:
        output_root = Path(temporary)
        for source in sources:
            output = output_root / f"{source.stem}.drawio"
            text = run_checked(
                [
                    "node",
                    str(base_root / "scripts" / "cli.js"),
                    str(source),
                    str(output),
                    "--validate",
                    "--strict-warnings",
                ]
            )
            for line in text.splitlines():
                if "recommends SVG export for paper-ready vector output" in line:
                    notices.add(line.strip())
    return {
        "base_root": str(base_root),
        "strict_examples": len(sources),
        "base_notices": sorted(notices),
    }


def validate_project_files(plugin: PluginConfig) -> None:
    required = (
        ROOT / "README.md",
        ROOT / "CHANGELOG.md",
        ROOT / "LICENSE",
        ROOT / "AGENTS.md",
        ROOT / "Makefile",
        ROOT / "evals" / "routing-boundaries.json",
        ROOT / "tools" / "verify_routing.py",
        plugin.path / ".codex-plugin" / "plugin.json",
        plugin.path / "LICENSE",
        plugin.path / "THIRD_PARTY_NOTICES.md",
        plugin.marketplace_path,
    )
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        raise VerificationError(f"required project files are missing: {missing}")


def validate_plugin(
    project: dict[str, Any], plugin: PluginConfig, skills: list[SkillConfig]
) -> dict[str, object]:
    manifest_path = plugin.path / ".codex-plugin" / "plugin.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected = {
        "name": plugin.name,
        "version": plugin.version,
        "skills": "./skills/",
    }
    mismatches = {
        field: {"expected": value, "actual": manifest.get(field)}
        for field, value in expected.items()
        if manifest.get(field) != value
    }
    if mismatches:
        raise VerificationError(f"plugin manifest mismatch: {mismatches}")
    if plugin.version != project["version"]:
        raise VerificationError("plugin version must match project.version")

    skill_root = (plugin.path / "skills").resolve()
    expected_names = {skill.name for skill in skills}
    actual_names = {path.name for path in skill_root.iterdir() if path.is_dir()}
    if actual_names != expected_names:
        raise VerificationError(
            f"plugin skill directories mismatch: expected {sorted(expected_names)}, "
            f"found {sorted(actual_names)}"
        )
    outside = [skill.name for skill in skills if skill.path.parent.resolve() != skill_root]
    if outside:
        raise VerificationError(f"configured skills must be direct plugin children: {outside}")

    marketplace = json.loads(plugin.marketplace_path.read_text(encoding="utf-8"))
    entries = [
        entry
        for entry in marketplace.get("plugins", [])
        if isinstance(entry, dict) and entry.get("name") == plugin.name
    ]
    if len(entries) != 1:
        raise VerificationError("repo marketplace must contain exactly one plugin entry")
    entry = entries[0]
    expected_source = f"./{plugin.path.relative_to(ROOT).as_posix()}"
    source = entry.get("source")
    if not isinstance(source, dict) or source.get("source") != "local":
        raise VerificationError("marketplace plugin source must be local")
    if source.get("path") != expected_source:
        raise VerificationError(
            f"marketplace source.path must be {expected_source!r}, got {source.get('path')!r}"
        )
    policy = entry.get("policy")
    if not isinstance(policy, dict) or {
        "installation",
        "authentication",
    } - set(policy):
        raise VerificationError("marketplace entry must include installation/authentication policy")
    return {
        "name": plugin.name,
        "version": plugin.version,
        "manifest": str(manifest_path.relative_to(ROOT)),
        "marketplace": str(plugin.marketplace_path.relative_to(ROOT)),
        "skills": sorted(expected_names),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify the academic figure skills project.")
    parser.add_argument("--with-base", action="store_true")
    parser.add_argument("--base", type=Path)
    parser.add_argument("--quick-validator", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        project, plugin, skills = load_project()
        validate_project_files(plugin)
        validator = find_quick_validator(args.quick_validator)
        summary: dict[str, Any] = {
            "status": "pass",
            "project": project["name"],
            "project_version": project["version"],
            "plugin": validate_plugin(project, plugin, skills),
            "routing": json.loads(run_checked([sys.executable, str(ROOT / "tools" / "verify_routing.py")])),
            "skills": {},
        }
        with tempfile.TemporaryDirectory(prefix="academic-figure-skills-") as temporary:
            cache_root = Path(temporary)
            for config in skills:
                skill_summary = validate_skill_structure(config)
                skill_summary.update(
                    validate_skill_runtime(config, validator, cache_root / config.name)
                )
                summary["skills"][config.name] = skill_summary

        if args.with_base:
            drawio = next(
                (config for config in skills if config.kind == "drawio-overlay"), None
            )
            if drawio is None:
                raise VerificationError("no drawio-overlay skill is configured")
            base = next((config for config in skills if config.kind == "drawio-base"), None)
            if base is None:
                raise VerificationError("no drawio-base skill is configured")
            summary["base_validation"] = validate_base(
                drawio.path, find_base(args.base, base.path)
            )
        else:
            summary["base_validation"] = "not_requested"

        print(json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True))
        return 0
    except (
        KeyError,
        OSError,
        TypeError,
        ValueError,
        VerificationError,
        json.JSONDecodeError,
        tomllib.TOMLDecodeError,
    ) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
