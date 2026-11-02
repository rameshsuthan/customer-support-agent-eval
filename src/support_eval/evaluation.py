"""Append-only experiments and paired scoring; no implicit provider retries."""
import fcntl
import hashlib
import json
import math
import os
import re
import time
import uuid
from decimal import Decimal
from pathlib import Path

import pandas as pd
from pydantic import BaseModel
from sklearn.metrics import precision_recall_fscore_support
from langsmith import get_current_run_tree, tracing_context
from .config import Settings
from .dataset import CATEGORIES

# Snapshot, not a live billing quote. Reverify before a paid pilot.
PRICES = {'input_per_million': 1.25, 'cached_input_per_million': .15,
          'output_per_million': 4.25, 'checked_date': '2026-11-02'}


def digest(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def cases_hash(cases: pd.DataFrame) -> str:
    fields = ['case_id', 'ticket_text', 'expected_category', 'source_case_id', 'source_file']
    payload = ''.join(json.dumps(r, sort_keys=True, ensure_ascii=False) + '\n'
                      for r in cases.sort_values('case_id')[fields].to_dict('records'))
    return hashlib.sha256(payload.encode()).hexdigest()


class RunSpec(BaseModel):
    run_id: str
    prompt_version: str
    prompt_hash: str
    dataset_version: str
    dataset_hash: str
    case_ids: list[str]
    case_fingerprints: dict[str, str]
    model: str
    settings_fingerprint: str
    model_settings: dict
    prices: dict
    langsmith_dataset_id: str | None = None


def make_run_spec(run_id: str, cases: pd.DataFrame, dataset_version: str,
                  prompt: str, settings: Settings, prompt_version: str = 'baseline') -> RunSpec:
    return RunSpec(run_id=run_id, prompt_version=prompt_version,
                   prompt_hash=hashlib.sha256(prompt.encode()).hexdigest(),
                   dataset_version=dataset_version, dataset_hash=cases_hash(cases),
                   case_ids=sorted(cases.case_id.tolist()), model=settings.model,
                   case_fingerprints={r.case_id: digest([r.ticket_text, r.expected_category]) for r in cases.itertuples()},
                   settings_fingerprint=digest(settings.model_settings()),
                   model_settings=settings.model_settings(), prices=PRICES.copy())


def can_start_call(recorded_usd: float, reserved_usd: float, next_bound_usd: float, budget_usd: float) -> bool:
    vals = [Decimal(str(x)) for x in (recorded_usd, reserved_usd, next_bound_usd, budget_usd)]
    if any(not x.is_finite() or x < 0 for x in vals):
        return False
    return sum(vals[:3]) <= vals[3]


def usage_cost(usage: dict | None, prices: dict = PRICES) -> float | None:
    if not usage or 'input_tokens' not in usage or 'output_tokens' not in usage:
        return None
    inp, out = usage['input_tokens'], usage['output_tokens']
    cached = (usage.get('input_token_details') or {}).get('cache_read', 0)
    if any(not isinstance(x, int) or isinstance(x, bool) or x < 0 for x in (inp, out, cached)) or cached > inp:
        return None
    # Reasoning is already part of output_tokens. Cached tokens are part of input_tokens.
    return float((Decimal(inp-cached)*Decimal(str(prices['input_per_million']))
                 + Decimal(cached)*Decimal(str(prices['cached_input_per_million']))
                 + Decimal(out)*Decimal(str(prices['output_per_million']))) / Decimal(1_000_000))


def append_json(path: Path, row: dict):
    with path.open('a') as stream:
        stream.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + '\n')
        stream.flush()
        os.fsync(stream.fileno())


def write_json(path: Path, data: dict):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(data, indent=2, allow_nan=False) + '\n')
    temporary.replace(path)


def ledger_spend(path: Path) -> float:
    if not path.exists():
        return 0.
    pending = set()
    total = Decimal(0)
    for line in path.read_text().splitlines():
        event = json.loads(line)
        if event['event'] == 'reserved':
            pending.add(event['attempt_id'])
        elif event['event'] == 'settled':
            cost = event.get('cost_usd')
            if cost is None:
                raise ValueError('Unresolved usage in ledger; reconcile billing before another paid call')
            amount = Decimal(str(cost))
            if not amount.is_finite() or amount < 0:
                raise ValueError('Invalid cost in ledger')
            total += amount
            pending.discard(event['attempt_id'])
    if pending:
        raise ValueError('Unresolved reservation from interrupted attempt; reconcile before continuing')
    return float(total)


def ensure_langsmith_dataset(cases: pd.DataFrame, manifest: dict, client) -> str:
    name = f"support-{manifest['version']}-{manifest['sha256'][:12]}"
    if client.has_dataset(dataset_name=name):
        dataset = client.read_dataset(dataset_name=name)
        examples = list(client.list_examples(dataset_id=dataset.id))
        existing = {e.inputs['case_id']: (e.inputs['ticket_text'], e.outputs['category']) for e in examples}
        expected = {r.case_id: (r.ticket_text, r.expected_category) for r in cases.itertuples()}
        if len(examples) != len(cases) or existing != expected:
            raise ValueError('LangSmith dataset contents differ from frozen cases')
        return str(dataset.id)
    dataset = client.create_dataset(dataset_name=name, description='Human-reviewed course exercise; synthetic data')
    client.create_examples(dataset_id=dataset.id,
                           inputs=[{'case_id': r.case_id, 'ticket_text': r.ticket_text} for r in cases.itertuples()],
                           outputs=[{'category': r.expected_category} for r in cases.itertuples()],
                           metadata=[{'dataset_hash': manifest['sha256']} for _ in range(len(cases))])
    return str(dataset.id)


def run_experiment(agent, cases: pd.DataFrame, run_spec: RunSpec, settings: Settings,
                   output_dir: Path, *, client=None, pilot: bool = False) -> pd.DataFrame:
    """client=None is for offline injected agents. Paid entrypoints must supply a client.

    Reserve the entire model input context at uncached pricing plus the output cap.
    This deliberately over-reserves per call; only reported usage is settled.
    Model cap and prices must be verified by the pilot before full experiments.
    """
    if client is not None:
        if not pilot and not settings.integration_verified:
            raise ValueError('Verify the integration pilot, prices, cap, usage and traces before a full run')
        if pilot and (len(cases) != 5 or set(cases.expected_category) != set(CATEGORIES)):
            raise ValueError('Pilot requires five reviewed cases covering all five categories')
        settings.require_credentials()
    if not re.fullmatch(r'[A-Za-z0-9_-]+', run_spec.run_id):
        raise ValueError('Invalid run ID')
    if cases_hash(cases) != run_spec.dataset_hash:
        raise ValueError('Dataset hash mismatch')
    if cases.case_id.duplicated().any() or sorted(cases.case_id.tolist()) != run_spec.case_ids:
        raise ValueError('Invalid case IDs')
    if digest(settings.model_settings()) != run_spec.settings_fingerprint:
        raise ValueError('Model settings differ from run spec')
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / 'usage.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        ledger = output_dir / 'usage.jsonl'
        spend = ledger_spend(ledger)
        folder = output_dir / 'runs' / run_spec.run_id
        folder.mkdir(parents=True, exist_ok=False)
        manifest = {**run_spec.model_dump(), 'status': 'running', 'expected_count': len(cases)}
        write_json(folder / 'manifest.json', manifest)
        lookup = cases.set_index('case_id').to_dict('index')
        rows, seen = [], set()
        halted = False
        # Muse Spark Open context bound from the model card; no guessed tokenizer needed.
        bound = (1_048_576 * run_spec.prices['input_per_million']
                 + settings.max_tokens * run_spec.prices['output_per_million']) / 1_000_000

        def target(inputs):
            nonlocal spend, halted
            if halted:
                return {'status': 'blocked', 'reason': 'Budget or usage requires review'}
            case_id = inputs['case_id']
            if case_id in seen or case_id not in lookup or inputs['ticket_text'] != lookup[case_id]['ticket_text']:
                halted = True
                raise ValueError('Unexpected or repeated example')
            seen.add(case_id)
            if not can_start_call(spend, 0, bound, settings.budget_usd):
                halted = True
                manifest['stop_reason'] = 'Budget guard'
                return {'status': 'blocked', 'reason': 'Budget guard'}
            case = lookup[case_id]
            attempt = str(uuid.uuid4())
            append_json(ledger, dict(event='reserved', attempt_id=attempt, run_id=run_spec.run_id, case_id=case_id, bound_usd=bound))
            start = time.perf_counter()
            row = dict(case_id=case_id, ticket_text=case['ticket_text'], expected_category=case['expected_category'],
                       run_id=run_spec.run_id, predicted_category=None, explanation=None, correct=False,
                       status='error', usage=None, cost_usd=None, error=None, trace_url=None, attempt_number=1)
            try:
                result = agent.invoke({'ticket_text': case['ticket_text']})
                row['usage'] = result.get('usage')
                row['cost_usd'] = usage_cost(row['usage'], run_spec.prices)
                prediction = result.get('prediction')
                if prediction and prediction.get('category') in CATEGORIES and prediction.get('explanation'):
                    row.update(status='ok', predicted_category=prediction['category'], explanation=prediction['explanation'])
                    row['correct'] = prediction['category'] == case['expected_category']
                else:
                    row.update(status='invalid', error='Invalid structured response')
            except Exception as exc:
                # Provider exceptions can contain headers/keys. Store type only.
                row['error'] = type(exc).__name__
            row['elapsed_seconds'] = time.perf_counter() - start
            current = get_current_run_tree()
            if current is not None:
                current.add_metadata({'case_id': case_id, 'run_id': run_spec.run_id,
                                      'prompt_version': run_spec.prompt_version,
                                      'dataset_hash': run_spec.dataset_hash,
                                      'expected_category': row['expected_category'], 'correct': row['correct']})
                try:
                    row['trace_url'] = current.get_url()
                except Exception:
                    pass
            append_json(folder / 'results.jsonl', row)
            append_json(ledger, dict(event='settled', attempt_id=attempt, cost_usd=row['cost_usd']))
            rows.append(row)
            if row['cost_usd'] is None or row['cost_usd'] > bound:
                halted = True
                manifest['stop_reason'] = 'Missing usage or exceeded reservation'
            else:
                spend += row['cost_usd']
            return row

        try:
            if client is not None:
                if not run_spec.langsmith_dataset_id:
                    raise ValueError('A verified LangSmith dataset is required')
                with tracing_context(enabled=True, client=client, project_name=settings.project):
                    experiment = client.evaluate(target, data=run_spec.langsmith_dataset_id,
                                                 experiment_prefix=run_spec.run_id, max_concurrency=1,
                                                 metadata=run_spec.model_dump(), blocking=True)
                    manifest['experiment_name'] = experiment.experiment_name
            else:
                with tracing_context(enabled=False):
                    for case in cases.to_dict('records'):
                        target({'case_id': case['case_id'], 'ticket_text': case['ticket_text']})
                        if halted:
                            break
        finally:
            manifest['status'] = 'complete' if len(rows) == len(cases) and not halted else 'incomplete'
            manifest['attempted_count'] = len(rows)
            write_json(folder / 'manifest.json', manifest)
        return pd.DataFrame(rows)


def validate_results(results: pd.DataFrame, run_spec: RunSpec):
    if results.empty or results.case_id.duplicated().any() or sorted(results.case_id.tolist()) != run_spec.case_ids:
        raise ValueError('Missing, duplicate, or unexpected case')
    if 'run_id' not in results or not results.run_id.eq(run_spec.run_id).all():
        raise ValueError('Results belong to a different run ID')
    for row in results.itertuples():
        if digest([row.ticket_text, row.expected_category]) != run_spec.case_fingerprints[row.case_id]:
            raise ValueError('Ticket text or reference label differs from frozen case')


def score_results(results: pd.DataFrame, run_spec: RunSpec) -> dict:
    validate_results(results, run_spec)
    if results.empty or results.case_id.duplicated().any():
        raise ValueError('Expected nonempty unique case results')
    if not results.expected_category.isin(CATEGORIES).all():
        raise ValueError('Invalid reference category')
    valid = results.status.eq('ok') & results.predicted_category.isin(CATEGORIES)
    predicted = results.predicted_category.where(valid, 'error')
    correct = predicted.eq(results.expected_category)
    precision, recall, f1, support = precision_recall_fscore_support(
        results.expected_category, predicted, labels=list(CATEGORIES), zero_division=0)
    matrix = pd.crosstab(results.expected_category, predicted).reindex(
        index=CATEGORIES, columns=[*CATEGORIES, 'error'], fill_value=0)
    costs = pd.to_numeric(results.cost_usd, errors='coerce')
    elapsed = pd.to_numeric(results.elapsed_seconds, errors='coerce')
    coverage = float(costs.notna().mean())
    return dict(case_count=len(results), accuracy=float(correct.mean()), macro_f1=float(f1.mean()),
                valid_response_rate=float(valid.mean()),
                p95_latency_seconds=float(elapsed.quantile(.95, interpolation='linear')) if elapsed.notna().all() else None,
                known_cost_usd=float(costs.sum()), cost_coverage=coverage,
                mean_cost_usd=float(costs.mean()) if coverage == 1 else None,
                per_category={c: dict(precision=float(p), recall=float(r), f1=float(f), support=int(s))
                              for c,p,r,f,s in zip(CATEGORIES, precision, recall, f1, support)},
                confusion_matrix=matrix.T.to_dict())


def compare_runs(baseline: pd.DataFrame, improved: pd.DataFrame,
                  baseline_spec: RunSpec, improved_spec: RunSpec) -> pd.DataFrame:
    for field in ('dataset_version', 'dataset_hash', 'case_ids', 'model', 'settings_fingerprint', 'prices'):
        if getattr(baseline_spec, field) != getattr(improved_spec, field):
            raise ValueError(f'Incompatible {field}')
    validate_results(baseline, baseline_spec)
    validate_results(improved, improved_spec)
    joined = baseline.merge(improved, on='case_id', suffixes=('_baseline', '_improved'), validate='one_to_one')
    for field in ('ticket_text', 'expected_category'):
        if not joined[f'{field}_baseline'].eq(joined[f'{field}_improved']).all():
            raise ValueError('Ticket text or reference label changed')
    a = joined.predicted_category_baseline.eq(joined.expected_category_baseline) & joined.status_baseline.eq('ok')
    b = joined.predicted_category_improved.eq(joined.expected_category_improved) & joined.status_improved.eq('ok')
    joined['outcome'] = ['unchanged_correct' if x and y else 'regression' if x else 'fixed' if y else 'unchanged_wrong'
                         for x,y in zip(a,b)]
    return joined
