from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_check(*arguments: str) -> subprocess.CompletedProcess[str]:
    environment = dict(os.environ, PYTHONPYCACHEPREFIX="/tmp/rfk-plugin-validation-pycache")
    return subprocess.run(["make", "check-plugin", *arguments], cwd=ROOT,
                          env=environment, text=True, capture_output=True, check=False)


def test_portable_plugin_check_without_external_validator() -> None:
    result = run_check("PLUGIN_VALIDATOR=")
    assert result.returncode == 0, result.stdout + result.stderr
    assert '"external_validator": "not_requested"' in result.stdout


def test_external_validator_success_failure_and_missing(tmp_path: Path) -> None:
    validator = tmp_path / "external validator.py"
    receipt = tmp_path / "receipt.json"
    validator.write_text(
        "import json, sys\nfrom pathlib import Path\n"
        f"Path({str(receipt)!r}).write_text(json.dumps(sys.argv[1:]))\n",
        encoding="utf-8",
    )
    result = run_check(f"PLUGIN_VALIDATOR={validator}")
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(receipt.read_text()) == [str(ROOT / "plugins/academic-figure-skills")]
    assert '"external_validator": "pass"' in result.stdout
    validator.write_text("raise SystemExit(7)\n", encoding="utf-8")
    result = run_check(f"PLUGIN_VALIDATOR={validator}")
    assert result.returncode != 0
    assert "external validator failed (7)" in result.stdout
    validator.unlink()
    result = run_check(f"PLUGIN_VALIDATOR={validator}")
    assert result.returncode != 0
    assert "external plugin validator not found" in result.stdout
