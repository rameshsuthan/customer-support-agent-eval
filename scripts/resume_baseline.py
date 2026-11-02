"""Explicit recovery of baseline-001; preserves failed attempts without retrying."""
import fcntl
import hashlib
import json
from pathlib import Path
from langsmith import Client
from support_eval.agent import build_agent
from support_eval.config import load_settings
from support_eval.dataset import load_frozen
from support_eval.evaluation import RunSpec, append_json, ledger_spend, run_experiment, score_results, write_json

root = Path(__file__).resolve().parents[1]
settings = load_settings(root / '.env')
folder = root / 'artifacts/runs/baseline-001'
spec = RunSpec.model_validate(json.loads((folder / 'manifest.json').read_text()))
prompt = (root / 'prompts/baseline.txt').read_text()
assert hashlib.sha256(prompt.encode()).hexdigest() == spec.prompt_hash
cases, _ = load_frozen(root / 'data/frozen/v1')
ledger = root / 'artifacts/usage.jsonl'
attempts = ['6d190a83-65cd-4ad4-b45e-c7e019822037', '4d421501-b4fd-4225-bd15-99e282002717']
with (root / 'artifacts/usage.lock').open('a') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    events = [json.loads(line) for line in ledger.read_text().splitlines()]
    for attempt in attempts:
        if not any(e['event'] == 'bounded_unknown' and e['attempt_id'] == attempt for e in events):
            assert any(e['event'] == 'settled' and e['attempt_id'] == attempt and e['cost_usd'] is None for e in events)
            append_json(ledger, dict(event='bounded_unknown', attempt_id=attempt,
                        reason='User approved continuation with $5 ceiling; retain original full-context reservation as budget exposure. Actual cost remains unknown.'))
    print('Conservative budget exposure before continuation:', ledger_spend(ledger), flush=True)
client = Client(api_key=settings.langsmith_api_key.get_secret_value(), api_url=settings.endpoint)
frame = run_experiment(build_agent(settings, prompt), cases, spec, settings, root / 'artifacts', client=client, resume=True)
manifest = json.loads((folder / 'manifest.json').read_text())
if manifest['status'] == 'complete':
    metrics = score_results(frame, spec)
    write_json(folder / 'metrics.json', metrics)
print(json.dumps({'status': manifest['status'], 'attempted': len(frame)}), flush=True)
