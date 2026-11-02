import pandas as pd
import pytest
from support_eval.dataset import make_review_table, freeze_dataset, load_frozen


def review():
    frame = pd.DataFrame([
        dict(source_case_id='a', ticket_text='Where is it?', original_label='order_status', source_file='source.csv'),
        dict(source_case_id='b', ticket_text='Cannot log in', original_label='account_help', source_file='source.csv'),
    ])
    return make_review_table(frame)


def approved():
    frame = review()
    frame['reviewed_label'] = frame.original_label
    frame['review_status'] = 'approved'
    return frame


def test_freeze_rejects_pending_labels(tmp_path):
    with pytest.raises(ValueError, match='review'):
        freeze_dataset(review(), tmp_path / 'frozen', 'v1')


def test_duplicate_id_conflict_rejected(tmp_path):
    frame = approved()
    frame.loc[1, 'case_id'] = frame.loc[0, 'case_id']
    with pytest.raises(ValueError, match='Duplicate'):
        freeze_dataset(frame, tmp_path / 'frozen', 'v1')


def test_invalid_category_rejected(tmp_path):
    frame = approved()
    frame.loc[0, 'reviewed_label'] = 'made_up'
    with pytest.raises(ValueError, match='label'):
        freeze_dataset(frame, tmp_path / 'frozen', 'v1')


def test_changed_text_changes_hash(tmp_path):
    frame = approved()
    first = freeze_dataset(frame, tmp_path / 'a', 'v1')
    reordered = freeze_dataset(frame.iloc[::-1], tmp_path / 'b', 'v1')
    assert first['sha256'] == reordered['sha256']
    frame.loc[0, 'ticket_text'] = 'Refund please'
    changed = freeze_dataset(frame, tmp_path / 'c', 'v1')
    assert first['sha256'] != changed['sha256']


def test_exclusions_require_reason_and_do_not_silently_drop(tmp_path):
    frame = approved()
    frame.loc[0, 'review_status'] = 'excluded'
    with pytest.raises(ValueError, match='reason'):
        freeze_dataset(frame, tmp_path / 'a', 'v1')
    frame.loc[0, 'review_note'] = 'Ambiguous without more context'
    result = freeze_dataset(frame, tmp_path / 'b', 'v1')
    assert result['case_count'] == 1
    assert len(result['exclusions']) == 1


def test_frozen_data_cannot_be_overwritten_or_tampered(tmp_path):
    folder = tmp_path / 'frozen'
    freeze_dataset(approved(), folder, 'v1')
    with pytest.raises(FileExistsError):
        freeze_dataset(approved(), folder, 'v1')
    cases, manifest = load_frozen(folder)
    assert len(cases) == manifest['case_count'] == 2
    (folder / 'tickets_v1.jsonl').write_text('{}\n')
    with pytest.raises(ValueError, match='hash'):
        load_frozen(folder)
