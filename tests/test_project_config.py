"""All engineering entrypoints share project metadata and reject invalid paths."""
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from project_config import load_project, ProjectConfigError
from package_skill import project_metadata
from package_plugin import plugin_metadata


def test_entrypoints_agree():
    project, plugin, skills = load_project(ROOT)
    assert project_metadata() == (project['version'], skills)
    assert plugin_metadata() == (plugin.name, plugin.version, plugin.path)


@pytest.mark.parametrize('mutation', ['escape', 'duplicate_path', 'duplicate_name', 'missing_field'])
def test_invalid_metadata_rejected(tmp_path, mutation):
    text = (ROOT / 'pyproject.toml').read_text()
    if mutation == 'escape':
        text = text.replace('path = "plugins/academic-figure-skills"', 'path = "../outside"', 1)
    elif mutation == 'duplicate_path':
        text = text.replace('path = "plugins/academic-figure-skills/skills/drawio-poster"',
                            'path = "plugins/academic-figure-skills/skills/drawio"')
    elif mutation == 'duplicate_name':
        text = text.replace('name = "drawio-poster"', 'name = "drawio"')
    else:
        text = text.replace('kind = "poster-overlay"', '')
    (tmp_path / 'pyproject.toml').write_text(text)
    with pytest.raises(ProjectConfigError):
        load_project(tmp_path)
