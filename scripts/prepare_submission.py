"""Recompute the approved three-run analysis from saved evidence; no API calls."""
import json
from pathlib import Path
import pandas as pd
from openpyxl import load_workbook
from support_eval.evaluation import RunSpec, score_results, compare_runs, ledger_spend, write_json

root=Path(__file__).resolve().parents[1]
ids=['baseline-001','baseline-2048-001','improved-2048-001']
labels=['Original 1024','Control 2048','Improved 2048']
runs=[]
frames=[]
specs=[]
for run_id,label in zip(ids,labels):
    folder=root/'artifacts/runs'/run_id
    manifest=json.loads((folder/'manifest.json').read_text())
    if manifest['status']!='complete':
        raise ValueError(f'Incomplete run: {run_id}; no final comparison allowed')
    spec=RunSpec.model_validate(manifest)
    frame=pd.read_json(folder/'results.jsonl',lines=True)
    metrics=score_results(frame,spec)
    write_json(folder/'metrics.json',metrics)
    frames.append(frame)
    specs.append(spec)
    runs.append(dict(run_id=run_id,label=label,max_tokens=spec.model_settings['max_tokens'],metrics=metrics))
comparisons={}
paired_rows=[]
changed_cases={}
for name,a,b in [('output_limit',0,1),('prompt',1,2)]:
    paired=compare_runs(frames[a],frames[b],specs[a],specs[b],comparison=name)
    paired.to_json(root/f'reports/{name}_comparison.jsonl',orient='records',lines=True)
    comparisons[name]=paired.outcome.value_counts().to_dict()
    changed_cases[name]=paired[paired.outcome.isin(['fixed','regression'])].to_dict('records')
    for r in paired.sort_values('case_id').to_dict('records'):
        paired_rows.append([name,r['case_id'],r['expected_category_baseline'],r['predicted_category_baseline'] if pd.notna(r['predicted_category_baseline']) else 'No prediction',r['predicted_category_improved'] if pd.notna(r['predicted_category_improved']) else 'No prediction',r['outcome']])

review=pd.read_csv(root/'data/frozen/v1/review_snapshot.csv',keep_default_na=False)
tag_column=next((c for c in review.columns if c in ('descriptive_tags','tags','review_tags','issue_tags')),None)
review_rows=[[r['case_id'],r['ticket_text'],r['original_label'],r['reviewed_label'],r['review_status'],r.get(tag_column,'') if tag_column else '',r['review_note']] for r in review.to_dict('records')]
annotations=json.loads((root/'reports/baseline_failure_annotations.json').read_text())
failures=[[r['case_id'],r['failure_group'],r['expected_category'],r['predicted_category'] or r['status'],r['annotation']] for r in annotations]
source=next((root/'data/source').glob('*.xlsx'))
wb=load_workbook(source)
empty={s.title:[c.coordinate for row in s for c in row if c.value==''] for s in wb}
all_results=[]
for frame in frames:
    all_results.extend(json.loads(frame.sort_values('case_id').to_json(orient='records')))
data=dict(source_file=str(source.relative_to(root)),source_sheet_count=len(wb.sheetnames),source_empty_cells=empty,
          runs=runs,results=all_results,review=review_rows,failures=failures,
          budget_exposure=ledger_spend(root/'artifacts/usage.jsonl'),comparisons=comparisons,paired_rows=paired_rows)
write_json(root/'reports/submission_data.json',data)
report='''# Customer support routing evaluation

We evaluated Fireworks Muse Spark Open on 100 human-reviewed synthetic e-commerce tickets, then isolated an output-limit increase from one focused routing-policy prompt change. A single-node LangGraph classifier returns one of five categories; LangSmith captures the model traces.

## Measured results

| Metric | Original 1024 | Control 2048 | Improved 2048 |
|---|---:|---:|---:|
'''
for title,key,fmt in [('Accuracy','accuracy','.1%'),('Macro F1','macro_f1','.3f'),('Valid responses','valid_response_rate','.1%'),('p95 latency (seconds)','p95_latency_seconds','.2f'),('Known cost (USD)','known_cost_usd','.6f'),('Cost coverage','cost_coverage','.0%')]:
    report+='| '+title+' | '+' | '.join(format(r['metrics'][key],fmt) for r in runs)+' |\n'
report+='\nAll metrics retain failed cases. Known cost excludes missing usage; a complete mean cost is unavailable when coverage is below 100%. Costs are token-based estimates, not invoices. p95 uses linear interpolation. Macro F1 averages the five fixed classes.\n\n'
for name,counts in comparisons.items():
    report+=f'### {name.replace("_"," ").title()} comparison\n\nPaired outcomes: '+', '.join(f'{k.replace("_"," ")}: {v}' for k,v in counts.items())+'.\n\n'
    for r in changed_cases[name]:
        before=r['predicted_category_baseline'] if pd.notna(r['predicted_category_baseline']) else r['status_baseline']
        after=r['predicted_category_improved'] if pd.notna(r['predicted_category_improved']) else r['status_improved']
        report+=f"- {r['case_id']}: {before} → {after}; expected {r['expected_category_baseline']}; {r['outcome']}.\n"
    if counts.get('regression',0)==0:
        report+='No regressions were observed in this run pair.\n'
    report+='\n'
report+='## Target assessment\n\n'
for r in runs:
    m=r['metrics']
    targets={'accuracy ≥95%':m['accuracy']>=.95,'macro F1 ≥0.90':m['macro_f1']>=.9,'valid responses 100%':m['valid_response_rate']==1,'p95 ≤15s':m['p95_latency_seconds']<=15,'mean cost ≤$0.02':None if m['mean_cost_usd'] is None else m['mean_cost_usd']<=.02}
    report+=r['label']+': '+', '.join(k+' '+('unknown' if v is None else 'met' if v else 'not met') for k,v in targets.items())+'.\n\n'
report+='''## Routing policy and intervention

The reviewed policy routes damaged products to product_issue even with an explicit refund demand. Non-delivery with an explicit refund request goes to refund_request. Packaging damage and missing manuals also belong to product_issue. No labels changed after viewing predictions.

The original run had four damaged-laptop/refund misroutes, one packaging/manual misroute, two output-cap failures and two provider HTTP 500 errors. The approved prompt edit states damaged-product priority and preserves non-delivery/refund routing. Packaging/manual wording remains unchanged. The control changes only max_tokens from 1024 to 2048; the prompt comparison holds max_tokens at 2048 and all other model settings fixed.

Provider recovery is not attributed to the prompt. Single runs remain subject to generation variability, provider load and execution timing even at temperature zero. Higher limits permit longer responses but do not force the model to use the full allowance.

## Provenance and limits

The frozen dataset contains 100 reviewed tickets in 25 synthetic seed families. The supplied CSV and workbook are different artifacts: 100 versus 150 tickets, with only one identical text among 100 shared IDs. Source outputs are never used as our predictions. Four source labels (t004–t007) were changed to refund_request during human review before freezing.

Source: The Gen Academy, https://github.com/The-Gen-Academy/4A-Customer-Support-Agent-Evaluation, revision ef517b274cf86a2c4fa8ae72fdc89b3dce80f41d. Reference workbook tabs are preserved separately from our result sheets. No license was found; materials remain a local course exercise.

The same dataset is used for diagnosis and reevaluation, so gains measure exercise-set improvement rather than independent generalization. Core-track scope is one focused prompt edit over 100 cases, plus the explicitly approved token-limit control. The general handout's 3–4 changes and 30–50 cases belong to the separate Own Use Case track; this project follows the Customer Support checklist. No LLM judge, fine-tuning, RAG or production deployment was attempted.

## Delivery and demo

The workbook, saved JSONL results, metrics and notebook contain the evidence. Analysis replay does not make model calls. Ramesh's narrated demo recording remains a separate submission action; no recording is claimed here.
'''
report+='\n## Interpretation and next step\n\n'
control,improved=runs[1]['metrics'],runs[2]['metrics']
report+=f"The focused prompt gained {(improved['accuracy']-control['accuracy'])*100:.1f} percentage points of accuracy, but valid-response rate changed by {(improved['valid_response_rate']-control['valid_response_rate'])*100:.1f} points. p95 latency changed by {improved['p95_latency_seconds']-control['p95_latency_seconds']:.2f} seconds and mean estimated cost by ${improved['mean_cost_usd']-control['mean_cost_usd']:.6f} per case.\n\n"
report+='All four targeted damaged-laptop cases were fixed and all four non-delivery/refund cases stayed correct. The two regressions, t058 and t083, exhausted2048 output tokens (2045 reasoning tokens); LangSmith confirms finish_reason=length. This supports the routing-priority hypothesis on this set, but fails the100% validity target. Next work would isolate reasoning/output-budget behavior on held-out tickets; no further experiment was run.\n\n'
known=sum(r['metrics']['known_cost_usd'] for r in runs)+json.loads((root/'artifacts/runs/pilot-001/metrics.json').read_text())['known_cost_usd']
report+=f'Known project estimate including pilot: ${known:.8f}, excluding two unknown-cost original HTTP500 calls. Conservative ledger exposure: ${data["budget_exposure"]:.8f}; approved ceiling $5.\n\n'
report+='## LangSmith evidence\n\n'
for run_id,frame in zip(ids,frames):
    seen=set()
    for url in frame.trace_url.dropna():
        prefix=url.split('/trace/')[0]; project=prefix.split('/projects/p/')[1]
        if project in seen:continue
        seen.add(project); workspace=prefix.split('/o/')[1].split('/')[0]
        report+=f'- [{run_id} experiment](https://smith.langchain.com/o/{workspace}/datasets/{specs[0].langsmith_dataset_id}/compare?selectedSessions={project})\n'
report+='\nRepresentative model-child traces were inspected for the targeted fix(t044), protected refund case(t004), and both regressions(t058,t083). Trace evidence is saved in reports/trace_evidence/improved_samples.json.\n'
(root/'reports/final_report.md').write_text(report)
print(json.dumps({'comparisons':comparisons,'budget_exposure':data['budget_exposure']}))
