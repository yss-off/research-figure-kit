"""Synthetic scoring fixtures only: these tests do not measure model routing."""
import copy
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from score_routing import export_prompts, load_gold, score_results


def fixture_results():
    gold, digest = load_gold(ROOT / 'evals/routing-boundaries.json')
    return {'schema_version': '1.0', 'gold_sha256': digest, 'run_id': 'synthetic-test',
            'model': 'synthetic-test', 'instruction_revision': 'synthetic-test',
            'observations': [{'id': case['id'], 'actual_route': case['expected_route'],
                              'evidence': 'Synthetic scorer fixture, not a model run'} for case in gold['cases']]}


def test_prompt_export_has_no_answers():
    prompts = export_prompts()
    assert all(set(case) == {'id', 'prompt'} for case in prompts['cases'])
    run = subprocess.run([sys.executable, str(ROOT / 'tools/score_routing.py'), '--prompts'],
                         capture_output=True, text=True, check=True)
    assert json.loads(run.stdout) == prompts


def test_complete_incomplete_and_mismatched_observations(tmp_path):
    results = fixture_results()
    assert score_results(results)['accuracy'] == 1
    results['observations'][0]['actual_route'] = 'clarify'
    report = score_results(results)
    assert len(report['mismatches']) == 1
    results['observations'].pop()
    report = score_results(results)
    assert report['status'] == 'incomplete' and report['accuracy'] is None
    receipt = tmp_path / 'results.json'
    receipt.write_text(json.dumps(results))
    run = subprocess.run([sys.executable, str(ROOT / 'tools/score_routing.py'), '--results', str(receipt)],
                         capture_output=True, text=True)
    assert run.returncode == 1
    assert json.loads(run.stdout) == report


@pytest.mark.parametrize('mutation', ['duplicate', 'unknown', 'hash', 'evidence', 'metadata'])
def test_invalid_results_rejected(mutation):
    results = copy.deepcopy(fixture_results())
    if mutation == 'duplicate':
        results['observations'].append(results['observations'][0])
    elif mutation == 'unknown':
        results['observations'][0]['id'] = 'unknown'
    elif mutation == 'hash':
        results['gold_sha256'] = '0' * 64
    elif mutation == 'evidence':
        results['observations'][0]['evidence'] = ''
    else:
        results['model'] = ''
    with pytest.raises(ValueError):
        score_results(results)
