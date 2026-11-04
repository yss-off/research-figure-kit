"""Exercise the actual package CLI twice, without writing into the checkout."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def test_independent_plugin_builds_are_identical(tmp_path: Path) -> None:
    outputs = []
    for index in range(2):
        environment = dict(os.environ, PYTHONHASHSEED=str(index + 1),
                           PYTHONPYCACHEPREFIX=str(tmp_path / "pycache"))
        run = subprocess.run(
            [sys.executable, str(ROOT / "tools/package_plugin.py"),
             "--output-dir", str(tmp_path / str(index))],
            cwd=ROOT, env=environment, capture_output=True, text=True, check=True,
        )
        receipt = json.loads(run.stdout)["package"]
        output = Path(receipt["path"])
        assert hashlib.sha256(output.read_bytes()).hexdigest() == receipt["sha256"]
        outputs.append(output)
    assert outputs[0].read_bytes() == outputs[1].read_bytes()
    with zipfile.ZipFile(outputs[0]) as archive:
        names = archive.namelist()
        prefix = "academic-figure-skills/"
        assert archive.testzip() is None
        assert len(names) == len(set(names)) == receipt["files"]
        assert all(name.startswith(prefix) for name in names)
        manifest = json.loads(archive.read(prefix + ".codex-plugin/plugin.json"))
        assert manifest["version"] == receipt["version"]
        assert prefix + "skills/drawio-academic-skills/scripts/figure_delivery.py" in names
        assert not any("__pycache__" in name or name.endswith(".pyc") for name in names)
