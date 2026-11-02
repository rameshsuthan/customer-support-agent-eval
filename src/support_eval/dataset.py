"""Preserve source labels and freeze explicitly reviewed cases."""
import hashlib
import json
import re
from pathlib import Path

import pandas as pd

CATEGORIES = ('order_status', 'refund_request', 'product_issue', 'account_help', 'other')


def load_source_cases(csv_path: Path) -> pd.DataFrame:
    data = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
    data = data.rename(columns={'id': 'source_case_id', 'true_category': 'original_label'})
    data['source_file'] = csv_path.name
    return data[['source_case_id', 'ticket_text', 'original_label', 'source_file']]


def make_review_table(cases: pd.DataFrame) -> pd.DataFrame:
    result = cases.copy()
    result.insert(0, 'case_id', ['course-' + str(x) for x in result.source_case_id])
    result['reviewed_label'] = ''
    result['review_status'] = 'pending'
    result['review_note'] = ''
    return result


def freeze_dataset(review: pd.DataFrame, output_dir: Path, version: str) -> dict:
    if not re.fullmatch(r'[A-Za-z0-9_-]+', version):
        raise ValueError('Invalid dataset version')
    review = review.fillna('')
    required = ['case_id', 'ticket_text', 'original_label', 'reviewed_label',
                'review_status', 'review_note', 'source_case_id', 'source_file']
    if set(required) - set(review.columns):
        raise ValueError('Missing review columns')
    if review.empty or not review.review_status.isin(['approved', 'excluded']).all():
        raise ValueError('Every case requires explicit human review')
    if review.case_id.duplicated().any():
        raise ValueError('Duplicate case IDs')
    if review.case_id.str.strip().eq('').any() or review.ticket_text.str.strip().eq('').any():
        raise ValueError('Empty case ID or ticket')
    exclusions = review[review.review_status == 'excluded']
    if exclusions.review_note.str.strip().eq('').any():
        raise ValueError('Excluded cases require a reason')
    included = review[review.review_status == 'approved'].copy()
    if included.empty or not included.reviewed_label.isin(CATEGORIES).all():
        raise ValueError('Approved cases require a valid reviewed label')
    changed = included.original_label != included.reviewed_label
    if included.loc[changed, 'review_note'].str.strip().eq('').any():
        raise ValueError('Changed label requires a review note')
    included = included.rename(columns={'reviewed_label': 'expected_category'})
    rows = included.sort_values('case_id')[['case_id', 'ticket_text', 'expected_category',
                                           'source_case_id', 'source_file']].to_dict('records')
    payload = ''.join(json.dumps(row, ensure_ascii=False, sort_keys=True) + '\n' for row in rows)
    filename = f'tickets_{version}.jsonl'
    manifest = dict(version=version, sha256=hashlib.sha256(payload.encode()).hexdigest(),
                    file=filename, case_count=len(rows),
                    category_counts=included.expected_category.value_counts().to_dict(),
                    exclusions=exclusions[['case_id', 'review_note']].to_dict('records'),
                    sources=sorted(included.source_file.unique().tolist()))
    output_dir.mkdir(parents=True, exist_ok=False)
    (output_dir / filename).write_text(payload)
    (output_dir / 'review_snapshot.csv').write_text(review.to_csv(index=False))
    (output_dir / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest


def load_frozen(folder: Path) -> tuple[pd.DataFrame, dict]:
    manifest = json.loads((folder / 'manifest.json').read_text())
    filename = manifest['file']
    if Path(filename).name != filename:
        raise ValueError('Invalid dataset file path')
    payload = (folder / filename).read_bytes()
    if hashlib.sha256(payload).hexdigest() != manifest['sha256']:
        raise ValueError('Dataset hash mismatch')
    frame = pd.DataFrame([json.loads(line) for line in payload.splitlines()])
    if len(frame) != manifest['case_count'] or frame.case_id.duplicated().any():
        raise ValueError('Dataset count or ID mismatch')
    return frame, manifest
