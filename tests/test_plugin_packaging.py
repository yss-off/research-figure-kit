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


def test_packages_ignore_host_write_permissions(tmp_path: Path) -> None:
    # Equivalent sources with different owner/group access must yield the same ZIP.
    sys.path.insert(0, str(ROOT / "tools"))
    from package_plugin import build_plugin
    from package_skill import SkillConfig, build_package

    sources = []
    for index, modes in enumerate(((0o600, 0o700), (0o664, 0o775))):
        source = tmp_path / f"source-{index}"
        source.mkdir()
        for name, mode in zip(("data.txt", "run.sh"), modes):
            file = source / name
            file.write_text("same content\n")
            file.chmod(mode)
        sources.append(source)
    for kind in ("plugin", "skill"):
        packages = []
        for index, source in enumerate(sources):
            out = tmp_path / f"{kind}-{index}"
            out.mkdir()
            receipt = (build_plugin("fixture", "1.0", source, out) if kind == "plugin"
                       else build_package(SkillConfig("fixture", "1.0", source, "fixture"), out))
            packages.append(Path(receipt["path"]))
        assert packages[0].read_bytes() == packages[1].read_bytes()
        with zipfile.ZipFile(packages[0]) as archive:
            assert archive.getinfo("fixture/data.txt").external_attr >> 16 == 0o644
            assert archive.getinfo("fixture/run.sh").external_attr >> 16 == 0o755
