"""Run the approved 2048-token control and focused prompt experiment once each."""
import json
from pathlib import Path
import pandas as pd
from langsmith import Client
from support_eval.agent import build_agent
from support_eval.config import load_settings
from support_eval.dataset import load_frozen
from support_eval.evaluation import (RunSpec, make_run_spec, ensure_langsmith_dataset,
    run_experiment, score_results, compare_runs, write_json, ledger_spend)

root = Path(__file__).resolve().parents[1]
settings = load_settings(root / '.env').model_copy(update={'max_tokens': 2048})
settings.require_credentials()
cases, dataset = load_frozen(root / 'data/frozen/v1')
client = Client(api_key=settings.langsmith_api_key.get_secret_value(), api_url=settings.endpoint,
                **({"workspace_id": settings.workspace_id} if settings.workspace_id else {}))
dataset_id = ensure_langsmith_dataset(cases, dataset, client)
completed = []
for run_id, prompt_file, version in [('baseline-2048-001', 'baseline.txt', 'baseline'),
                                     ('improved-2048-001', 'improved.txt', 'refund-priority-v1')]:
    prompt = (root / 'prompts' / prompt_file).read_text()
    spec = make_run_spec(run_id, cases, dataset['version'], prompt, settings, version)
    spec.langsmith_dataset_id = dataset_id
    folder = root / 'artifacts/runs' / run_id
    if folder.exists():
        manifest = json.loads((folder/'manifest.json').read_text())
        if RunSpec.model_validate(manifest) != spec:
            raise ValueError('Saved experiment differs from requested spec')
        if manifest['status'] != 'complete':
            raise ValueError('Incomplete experiment requires explicit reviewed recovery')
        frame = pd.read_json(folder/'results.jsonl', lines=True)
    else:
        print(json.dumps({'starting':run_id,'max_tokens':settings.max_tokens,
                          'budget_exposure_usd':ledger_spend(root/'artifacts/usage.jsonl')}), flush=True)
        frame = run_experiment(build_agent(settings, prompt), cases, spec, settings,
                               root/'artifacts', client=client)
        manifest = json.loads((folder/'manifest.json').read_text())
        if manifest['status'] != 'complete':
            print(json.dumps({'stopped':run_id,'attempted':len(frame),'reason':manifest.get('stop_reason')}), flush=True)
            break
    metrics = score_results(frame,spec)
    write_json(folder/'metrics.json',metrics)
    completed.append((frame,spec))
    print(json.dumps({'completed':run_id,'metrics':metrics}), flush=True)
if len(completed)==2:
    pairs = compare_runs(completed[0][0],completed[1][0],completed[0][1],completed[1][1])
    pairs.to_json(root/'reports/prompt_comparison.jsonl',orient='records',lines=True)
    print('Both approved experiments completed.',flush=True)
