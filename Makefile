PYTHON ?= python3
PLUGIN_ROOT := plugins/academic-figure-skills
SKILLS_ROOT := $(PLUGIN_ROOT)/skills

.PHONY: test test-routing check check-base check-plugin package package-plugin package-skills package-base package-academic package-drawio package-scientific

test:
	PYTHONPYCACHEPREFIX=/tmp/academic-figure-skills-pycache $(PYTHON) $(SKILLS_ROOT)/drawio-poster/evals/smoke_test.py
	node $(SKILLS_ROOT)/drawio/scripts/cli.js --help >/dev/null
	PYTHONPYCACHEPREFIX=/tmp/academic-figure-skills-pycache $(PYTHON) $(SKILLS_ROOT)/drawio-academic-skills/evals/smoke_test.py
	PYTHONPYCACHEPREFIX=/tmp/academic-figure-skills-pycache MPLCONFIGDIR=/tmp/academic-figure-skills-mpl $(PYTHON) $(SKILLS_ROOT)/scientific-visualization/evals/smoke_test.py

test-routing:
	$(PYTHON) tools/verify_routing.py

check:
	$(PYTHON) tools/verify_project.py

check-base:
	$(PYTHON) tools/verify_project.py --with-base

check-plugin:
	$(PYTHON) /home/yss/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py $(PLUGIN_ROOT)

package: package-plugin

package-plugin:
	$(PYTHON) tools/package_plugin.py --force

package-skills:
	$(PYTHON) tools/package_skill.py --all --force

package-base:
	$(PYTHON) tools/package_skill.py --skill drawio --force

package-academic:
	$(PYTHON) tools/package_skill.py --skill drawio-academic-skills --force

package-drawio: package-academic

package-scientific:
	$(PYTHON) tools/package_skill.py --skill scientific-visualization --force
