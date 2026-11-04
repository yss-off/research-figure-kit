#!/usr/bin/env python3
"""Portable repository plugin checks, with an optional external validator."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from verify_project import (
    VerificationError,
    load_project,
    validate_plugin,
    validate_project_files,
    validate_skill_structure,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plugin", type=Path)
    parser.add_argument("--validator", type=Path, help="Optional external Python validator")
    args = parser.parse_args()
    try:
        project, plugin, skills = load_project()
        if args.plugin.resolve() != plugin.path:
            raise VerificationError("plugin path must match pyproject.toml")
        validate_project_files(plugin)
        summary = validate_plugin(project, plugin, skills)
        for skill in skills:
            validate_skill_structure(skill)
        external = "not_requested"
        if args.validator is not None:
            validator = args.validator.expanduser().resolve()
            if not validator.is_file():
                raise VerificationError(f"external plugin validator not found: {validator}")
            result = subprocess.run(
                [sys.executable, str(validator), str(plugin.path)],
                text=True, capture_output=True, check=False,
            )
            if result.returncode:
                raise VerificationError(
                    f"external validator failed ({result.returncode}): "
                    f"{result.stdout}\n{result.stderr}"
                )
            external = "pass"
        print(json.dumps({
            "status": "pass", "plugin": summary,
            "scope": "Repository manifest, marketplace, and skill structure contracts only; not host execution or public submission approval.",
            "external_validator": external,
        }, indent=2))
        return 0
    except (OSError, KeyError, TypeError, ValueError, VerificationError) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
