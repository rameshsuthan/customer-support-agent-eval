import json
from pathlib import Path
import pandas as pd
import pytest
from support_eval.config import Settings
from support_eval.evaluation import RunSpec, run_experiment, can_start_call, usage_cost, make_run_spec


def cases():
    return pd.DataFrame([dict(case_id='a', ticket_text='Where is it?', expected_category='order_status', source_case_id='a', source_file='x'),
                         dict(case_id='b', ticket_text='Refund', expected_category='refund_request', source_case_id='b', source_file='x')])


class FakeAgent:
    def __init__(self, result=None, failure=None):
        self.result, self.failure = result, failure
    def invoke(self, data):
        if self.failure:
            raise self.failure
        return self.result


def good():
    return dict(prediction={'category': 'order_status', 'explanation': 'Tracking request'},
                usage={'input_tokens': 100, 'output_tokens': 20, 'total_tokens': 120})


def spec():
    return make_run_spec('baseline-test', cases(), 'v1', 'prompt', Settings())


@pytest.mark.parametrize('failure', [TimeoutError('secret details'), RuntimeError('provider')])
def test_provider_failure_retained_and_unknown_cost_stops(tmp_path, failure):
    frame = run_experiment(FakeAgent(failure=failure), cases(), spec(), Settings(), tmp_path)
    assert len(frame) == 1
    assert frame.iloc[0].status == 'error'
    assert frame.iloc[0].predicted_category is None
    assert not frame.iloc[0].correct
    assert frame.iloc[0].cost_usd is None
    assert 'secret details' not in (tmp_path/'runs/baseline-test/results.jsonl').read_text()


def test_missing_usage_halts_calls_and_persists(tmp_path):
    frame = run_experiment(FakeAgent(result={**good(), 'usage': None}), cases(), spec(), Settings(), tmp_path)
    assert len(frame) == 1
    assert (tmp_path / 'usage.jsonl').exists()
    assert json.loads((tmp_path/'runs/baseline-test/manifest.json').read_text())['status'] == 'incomplete'


def test_completed_run_refuses_reuse(tmp_path):
    run_experiment(FakeAgent(result=good()), cases(), spec(), Settings(), tmp_path)
    with pytest.raises(FileExistsError):
        run_experiment(FakeAgent(result=good()), cases(), spec(), Settings(), tmp_path)


def test_budget_exact_boundary():
    assert can_start_call(2.90, 0, .10, 3)
    assert not can_start_call(2.90, 0, .11, 3)


def test_usage_does_not_double_count_cache_or_reasoning():
    usage = dict(input_tokens=1000, output_tokens=500,
                 input_token_details={'cache_read': 200}, output_token_details={'reasoning': 400})
    assert usage_cost(usage) == pytest.approx(.003155)


def test_interrupted_reservation_blocks_new_calls(tmp_path):
    (tmp_path/'usage.jsonl').write_text(json.dumps({'event': 'reserved', 'attempt_id': 'lost', 'bound_usd': 1.4})+'\n')
    with pytest.raises(ValueError, match='Unresolved'):
        run_experiment(FakeAgent(result=good()), cases(), spec(), Settings(), tmp_path)


def test_case_change_rejected_before_execution(tmp_path):
    changed = cases()
    changed.loc[0, 'ticket_text'] = 'different'
    with pytest.raises(ValueError, match='hash'):
        run_experiment(FakeAgent(result=good()), changed, spec(), Settings(), tmp_path)


def test_unverified_full_run_blocked_before_provider(tmp_path):
    with pytest.raises(ValueError, match='integration'):
        run_experiment(FakeAgent(result=good()), cases(), spec(), Settings(), tmp_path, client=object())
    assert not (tmp_path/'usage.jsonl').exists()
