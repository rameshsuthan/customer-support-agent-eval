# Customer support routing evaluation

We evaluated Fireworks Muse Spark Open on 100 human-reviewed synthetic e-commerce tickets, then isolated an output-limit increase from one focused routing-policy prompt change. A single-node LangGraph classifier returns one of five categories; LangSmith captures the model traces.

## Measured results

| Metric | Original 1024 | Control 2048 | Improved 2048 |
|---|---:|---:|---:|
| Accuracy | 91.0% | 96.0% | 98.0% |
| Macro F1 | 0.927 | 0.962 | 0.990 |
| Valid responses | 96.0% | 100.0% | 98.0% |
| p95 latency (seconds) | 16.86 | 11.65 | 13.21 |
| Known cost (USD) | 0.239355 | 0.259043 | 0.279014 |
| Cost coverage | 98% | 100% | 100% |

All metrics retain failed cases. Known cost excludes missing usage; a complete mean cost is unavailable when coverage is below 100%. Costs are token-based estimates, not invoices. p95 uses linear interpolation. Macro F1 averages the five fixed classes.

### Output Limit comparison

Paired outcomes: unchanged correct: 91, fixed: 5, unchanged wrong: 4.

- course-t026: error → refund_request; expected refund_request; fixed.
- course-t015: invalid → order_status; expected order_status; fixed.
- course-t055: error → product_issue; expected product_issue; fixed.
- course-t059: other → product_issue; expected product_issue; fixed.
- course-t058: invalid → product_issue; expected product_issue; fixed.
No regressions were observed in this run pair.

### Prompt comparison

Paired outcomes: unchanged correct: 94, fixed: 4, regression: 2.

- course-t047: refund_request → product_issue; expected product_issue; fixed.
- course-t083: other → invalid; expected other; regression.
- course-t045: refund_request → product_issue; expected product_issue; fixed.
- course-t046: refund_request → product_issue; expected product_issue; fixed.
- course-t044: refund_request → product_issue; expected product_issue; fixed.
- course-t058: product_issue → invalid; expected product_issue; regression.

## Target assessment

Original 1024: accuracy ≥95% not met, macro F1 ≥0.90 met, valid responses 100% not met, p95 ≤15s not met, mean cost ≤$0.02 unknown.

Control 2048: accuracy ≥95% met, macro F1 ≥0.90 met, valid responses 100% met, p95 ≤15s met, mean cost ≤$0.02 met.

Improved 2048: accuracy ≥95% met, macro F1 ≥0.90 met, valid responses 100% not met, p95 ≤15s met, mean cost ≤$0.02 met.

## Routing policy and intervention

The reviewed policy routes damaged products to product_issue even with an explicit refund demand. Non-delivery with an explicit refund request goes to refund_request. Packaging damage and missing manuals also belong to product_issue. No labels changed after viewing predictions.

The original run had four damaged-laptop/refund misroutes, one packaging/manual misroute, two output-cap failures and two provider HTTP 500 errors. The approved prompt edit states damaged-product priority and preserves non-delivery/refund routing. Packaging/manual wording remains unchanged. The control changes only max_tokens from 1024 to 2048; the prompt comparison holds max_tokens at 2048 and all other model settings fixed.

Provider recovery is not attributed to the prompt. Single runs remain subject to generation variability, provider load and execution timing even at temperature zero. Higher limits permit longer responses but do not force the model to use the full allowance.

## Provenance and limits

The frozen dataset contains 100 reviewed tickets in 25 synthetic seed families. The supplied CSV and workbook are different artifacts: 100 versus 150 tickets, with only one identical text among 100 shared IDs. Source outputs are never used as our predictions. Four source labels (t004–t007) were changed to refund_request during human review before freezing.

Source: The Gen Academy, https://github.com/The-Gen-Academy/4A-Customer-Support-Agent-Evaluation, revision ef517b274cf86a2c4fa8ae72fdc89b3dce80f41d. Reference workbook tabs are preserved separately from our result sheets. No license was found; materials remain a local course exercise.

The same dataset is used for diagnosis and reevaluation, so gains measure exercise-set improvement rather than independent generalization. Core-track scope is one focused prompt edit over 100 cases, plus the explicitly approved token-limit control. This differs from the generic rubric's 3–4 changes and 30–50 cases. No LLM judge, fine-tuning, RAG or production deployment was attempted.

## Delivery and demo

The workbook, saved JSONL results, metrics and notebook contain the evidence. Analysis replay does not make model calls. Ramesh's narrated demo recording remains a separate submission action; no recording is claimed here.

## Interpretation and next step

The focused prompt gained 2.0 percentage points of accuracy, but valid-response rate changed by -2.0 points. p95 latency changed by 1.56 seconds and mean estimated cost by $0.000200 per case.

All four targeted damaged-laptop cases were fixed and all four non-delivery/refund cases stayed correct. The two regressions, t058 and t083, exhausted 2048 output tokens (2045 reasoning tokens); LangSmith confirms finish_reason=length. This supports the routing-priority hypothesis on this set, but fails the 100% validity target. Next work would isolate reasoning/output-budget behavior on held-out tickets; no further experiment was run.

Known project estimate including pilot: $0.79069535, excluding two unknown-cost original HTTP500 calls. Conservative ledger exposure: $3.42083935; approved ceiling $5.

## LangSmith evidence

- [baseline-001 experiment](https://smith.langchain.com/o/82c36783-971e-46c1-862e-a27d43bbcba3/datasets/892c6169-ac98-4d08-b4be-8363f254cc11/compare?selectedSessions=efa627bd-6463-4b5e-9044-6d1319cecbaa)
- [baseline-001 experiment](https://smith.langchain.com/o/82c36783-971e-46c1-862e-a27d43bbcba3/datasets/892c6169-ac98-4d08-b4be-8363f254cc11/compare?selectedSessions=15f3f758-548f-4fd1-b994-c71bdd40d11b)
- [baseline-001 experiment](https://smith.langchain.com/o/82c36783-971e-46c1-862e-a27d43bbcba3/datasets/892c6169-ac98-4d08-b4be-8363f254cc11/compare?selectedSessions=f512963c-b927-4465-911c-4f2324bac698)
- [baseline-2048-001 experiment](https://smith.langchain.com/o/82c36783-971e-46c1-862e-a27d43bbcba3/datasets/892c6169-ac98-4d08-b4be-8363f254cc11/compare?selectedSessions=fbf15121-6924-4b0a-9c37-de46208b0b45)
- [improved-2048-001 experiment](https://smith.langchain.com/o/82c36783-971e-46c1-862e-a27d43bbcba3/datasets/892c6169-ac98-4d08-b4be-8363f254cc11/compare?selectedSessions=a6ba6566-3751-417b-95cc-0de7e769182f)

Representative model-child traces were inspected for the targeted fix (t044), protected refund case (t004), and both regressions (t058,t083). Trace evidence is saved in reports/trace_evidence/improved_samples.json.
