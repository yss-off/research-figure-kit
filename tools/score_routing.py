#!/usr/bin/env python3
"""Export unlabeled prompts or score recorded routing observations offline; never run a model."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOLD = ROOT / 'evals/routing-boundaries.json'


def load_gold(path: Path):
    raw = path.read_bytes()
    document = json.loads(raw)
    cases = document['cases']
    if not cases or len({case['id'] for case in cases}) != len(cases):
        raise ValueError('gold cases must be nonempty with unique IDs')
    return document, hashlib.sha256(raw).hexdigest()


def export_prompts(path: Path = GOLD):
    gold, digest = load_gold(path)
    return {'schema_version': '1.0', 'gold_sha256': digest,
            'cases': [{'id': case['id'], 'prompt': case['prompt']} for case in gold['cases']]}


def score_results(results: dict, path: Path = GOLD):
    gold, digest = load_gold(path)
    if results.get('schema_version') != '1.0' or results.get('gold_sha256') != digest:
        raise ValueError('result schema or gold hash does not match the current case set')
    for field in ('run_id', 'model', 'instruction_revision'):
        if not isinstance(results.get(field), str) or not results[field].strip():
            raise ValueError(f'{field} must record the evaluated run configuration')
    expected = {case['id']: case['expected_route'] for case in gold['cases']}
    observations = results.get('observations')
    if not isinstance(observations, list):
        raise ValueError('observations must be a list')
    seen, mismatches = set(), []
    correct = 0
    for observation in observations:
        if not isinstance(observation, dict):
            raise ValueError('each observation must be an object')
        case_id = observation.get('id')
        if not isinstance(case_id, str) or case_id not in expected or case_id in seen:
            raise ValueError(f'unknown or duplicate observation ID: {case_id}')
        actual = observation.get('actual_route')
        if actual not in gold['routes']:
            raise ValueError(f'unsupported actual route for {case_id}')
        evidence = observation.get('evidence')
        if not isinstance(evidence, str) or not evidence.strip():
            raise ValueError(f'{case_id} requires an observation or trace reference')
        seen.add(case_id)
        if actual == expected[case_id]:
            correct += 1
        else:
            mismatches.append({'id': case_id, 'expected_route': expected[case_id], 'actual_route': actual})
    missing = sorted(set(expected) - seen)
    return {'schema_version': '1.0', 'status': 'incomplete' if missing else 'scored',
            'run_id': results['run_id'], 'model': results['model'],
            'instruction_revision': results['instruction_revision'], 'gold_sha256': digest,
            'total': len(expected), 'observed': len(seen), 'correct': correct,
            'accuracy': correct / len(expected) if not missing else None,
            'missing': missing, 'mismatches': mismatches,
            'notice': 'Scores supplied observations only; no model was run and trace authenticity was not verified.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--prompts', action='store_true', help='Emit prompts without gold labels or reasons')
    mode.add_argument('--results', type=Path, help='Score an existing observation JSON')
    args = parser.parse_args(argv)
    try:
        if args.prompts:
            report = export_prompts()
        else:
            report = score_results(json.loads(args.results.read_text(encoding='utf-8')))
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0 if args.prompts or (not report['missing'] and not report['mismatches']) else 1
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        print(json.dumps({'status': 'fail', 'error': str(exc)}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
