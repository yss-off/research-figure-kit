from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_project_validation_including_smoke_routing_and_base() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools/verify_project.py"),
         "--with-base", "--no-quick-validator"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    assert result.returncode == 0, output
    summary = json.loads(result.stdout)
    assert summary["status"] == "pass"
    assert summary["base_validation"] != "not_requested"
    assert all(skill["skill_validation"] == "not_available" for skill in summary["skills"].values())
    assert all(skill.get("smoke_tests") == "pass" for name, skill in summary["skills"].items()
               if name != "drawio")
