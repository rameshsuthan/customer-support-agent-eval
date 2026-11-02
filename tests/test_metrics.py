import pandas as pd
import pytest
from support_eval.evaluation import score_results, compare_runs, make_run_spec
from support_eval.config import Settings


def rows():
    return pd.DataFrame([
        dict(run_id='v1', case_id='a', ticket_text='A', expected_category='order_status', predicted_category='order_status', status='ok', elapsed_seconds=1., cost_usd=.001),
        dict(run_id='v1', case_id='b', ticket_text='B', expected_category='refund_request', predicted_category='refund_request', status='ok', elapsed_seconds=2., cost_usd=.001),
        dict(run_id='v1', case_id='c', ticket_text='C', expected_category='product_issue', predicted_category='other', status='ok', elapsed_seconds=3., cost_usd=.001),
        dict(run_id='v1', case_id='d', ticket_text='D', expected_category='account_help', predicted_category=None, status='error', elapsed_seconds=60., cost_usd=None),
    ])


def test_error_counts_in_accuracy_denominator():
    metrics = score_results(rows(), specs()[0])
    assert metrics['accuracy'] == .5
    assert metrics['valid_response_rate'] == .75
    assert metrics['per_category']['account_help']['recall'] == 0
    assert metrics['confusion_matrix']['account_help']['error'] == 1
    assert metrics['p95_latency_seconds'] == pytest.approx(51.45)


def test_unknown_cost_is_not_zero():
    metrics = score_results(rows(), specs()[0])
    assert metrics['mean_cost_usd'] is None
    assert metrics['cost_coverage'] == .75
    assert metrics['known_cost_usd'] == .003


def specs():
    data = rows().assign(source_case_id=lambda f: f.case_id, source_file='x')
    return make_run_spec('v1', data, 'v1', 'first', Settings()), make_run_spec('v2', data, 'v1', 'second', Settings())


def test_paired_counts_include_regressions():
    base = rows()
    improved = rows().assign(run_id="v2")
    improved.loc[0, 'predicted_category'] = 'other'
    improved.loc[2, 'predicted_category'] = 'product_issue'
    a,b = specs()
    result = compare_runs(base, improved.iloc[::-1], a, b)
    assert result.outcome.value_counts().to_dict() == {'regression':1, 'unchanged_correct':1, 'fixed':1, 'unchanged_wrong':1}


def test_missing_case_rejected():
    a,b = specs()
    with pytest.raises(ValueError, match='case'):
        compare_runs(rows(), rows().iloc[:3], a,b)


def test_mismatched_dataset_or_model_rejected():
    a,b = specs()
    b = b.model_copy(update={'model': 'different'})
    with pytest.raises(ValueError, match='model'):
        compare_runs(rows(), rows(), a,b)


def test_label_change_rejected_even_with_same_manifest():
    a,b = specs()
    changed = rows()
    changed.loc[0, 'expected_category'] = 'other'
    with pytest.raises(ValueError, match='label'):
        compare_runs(rows(), changed.assign(run_id='v2'), a,b)


def test_scoring_rejects_missing_frozen_cases():
    with pytest.raises(ValueError, match='case'):
        score_results(rows().iloc[:1], specs()[0])


def test_unrelated_run_id_rejected():
    a,b = specs()
    with pytest.raises(ValueError, match='run ID'):
        compare_runs(rows().assign(run_id='unrelated'), rows().assign(run_id='v2'), a,b)


def test_identical_label_edits_in_both_frames_rejected():
    a,b = specs()
    edited = rows()
    edited.loc[0,'expected_category'] = 'other'
    with pytest.raises(ValueError, match='label'):
        compare_runs(edited, edited.assign(run_id='v2'), a,b)
