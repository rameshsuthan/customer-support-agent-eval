# Customer Support Routing Evaluation — Design

Date: November 2, 2026
Status: Approved for implementation; human review amendments below supersede initial policy choices. No paid runs yet.

## Intent and agreed scope

Build a local, notebook-led evaluation of an e-commerce ticket-routing agent. Explain why classification fails, test one focused prompt change, and report measured improvements and regressions. The learner is Ramesh; the operational user is a support team that needs tickets sent to the team responsible for the underlying problem.

Agreed choices: Customer Support core track; local execution; Fireworks AI with Muse Spark Open; a separate LangSmith account; no optional LLM judge. Ramesh initially selected underlying-problem routing, then explicitly refined non-delivery refund requests to `refund_request` while retaining `product_issue` for damaged-product refund requests.

The project is an original evaluation using attributed course materials. Reusing the five-category task, source tickets, workbook layout, and simple LangGraph structure is appropriate. Course annotations, improved prompts, and published results must not be presented as our own analysis or measurements. Any reused code must retain applicable license notices; inspect the source license before redistribution.

## Approaches and decision

1. **Adapt the supplied single-node classifier and build our evaluation around it.** Lowest setup cost, fits the course, leaves time for label review and failure analysis. This follows the approach selected in conversation, updated to Fireworks.
2. **Build a new support system with retrieval, tools, or multiple agents.** More functionality, but changes the task and diverts work from evaluation; excluded from this core project.
3. **Use only the supplied spreadsheet results.** Useful practice, but insufficient for our own measured prompt improvement and the general handout's trace requirement.

Use approach 1. Keep the notebook as the learning narrative and place reusable evaluation logic in a few small Python modules.

## Routing policy

Return exactly one of `order_status`, `refund_request`, `product_issue`, `account_help`, `other`, plus a concise decision explanation.

- `order_status`: tracking, delivery timing, or non-delivery without an explicit refund request. Human review on November 2 routes non-delivery plus explicit refund to `refund_request` (course-t004–t007).
- `product_issue`: broken, wrong, defective, incomplete, or misdescribed goods, including an explicit refund request because of that problem.
- `refund_request`: refund/cancellation requests, non-delivery with an explicit refund request, and follow-up on a refund already initiated. Damaged-product refund requests remain `product_issue`, explicitly confirmed for course-t044–t047.
- `account_help`: login, password, profile/address/payment-method changes, and account/session failures preventing checkout.
- `other`: general questions, stock/discount inquiries, feedback, and requests outside the above categories.

Policy clarification is a ground-truth decision, not an automatic prompt improvement. Review ambiguous combinations against the full ticket before freezing labels. Unresolvable cases are marked for review and excluded before freezing, with the exclusion reason retained. The baseline prompt will use the starter's simple category descriptions, attributed and adapted only for valid structured output. The improved prompt is written only after our baseline failure analysis; do not copy the supplied improved prompt. Both are scored against the same documented policy.

## Dataset and human review

Use the 100 fixed ticket texts in the repository's `results_v1.csv` as the initial candidate set rather than regenerating paraphrases on each run. The starter notebook uses 25 hand-written seeds and generated variations. Document this synthetic origin and correlated seed families; do not describe it as real customer data or independent production evidence.

The workbook handout mentions 29 failed rows, while the repository CSV has 8 baseline errors and 100 rows. Inspect the workbook and CSV independently, record source revision and file hashes, and reconcile ticket texts/IDs. Do not combine records by position or assume similarly named IDs identify identical tickets. Preserve each source file unchanged. Our fresh baseline defines our failure population; the supplied 29-row exercise remains a reference when it differs.

Maintain a review table containing `case_id`, `ticket_text`, `original_label`, `reviewed_label`, `review_status`, `review_note`, `source_file`, and `source_case_id`. Assistant suggestions are proposals until Ramesh reviews them. Review all included labels before scoring; never claim autonomous assistant labels are human-reviewed. Corrections go in this table, preserving the original workbook fields as required by the track handout.

Freeze the approved dataset with a version and SHA-256 hash. Input to the classifier contains only ticket text and the prompt, never labels or annotations. Upload the same frozen cases and reference labels to a versioned LangSmith dataset. Baseline and improved experiments use the same examples; changing a label requires a new dataset version and rerunning both experiments.

All cases may be used for diagnosis and paired reevaluation in the core exercise. This measures improvement on the reviewed exercise set, not held-out generalization. Disclose that limitation, especially because starter failure examples and solution prompts were inspected during planning. A future independent holdout is out of scope.

## Architecture and proposed files

Use Python 3.11 or 3.12 in `.venv`, JupyterLab, LangGraph, `langchain-fireworks`, LangSmith, Pydantic, pandas, scikit-learn, openpyxl, python-dotenv, and pytest. Check the installed interpreter first; choose and record compatible versions during setup rather than inventing version pins now.

| File or directory | Responsibility |
|---|---|
| `README.md`, `.gitignore`, `.env.example`, `requirements.txt`, `requirements-lock.txt` | Reproducible local setup, credentials placeholders, dependency record |
| `src/support_eval/config.py` | Validated provider, tracing, and budget configuration |
| `src/support_eval/dataset.py` | Source import, review validation, frozen dataset and hash |
| `src/support_eval/agent.py` | Pydantic prediction, Fireworks model, single-node LangGraph |
| `src/support_eval/evaluation.py` | Experiments, result validation, scoring, paired comparison, usage ledger |
| `notebooks/customer_support_evaluation.ipynb` | Guided preparation, pilot, baseline, review, improvement, and report |
| `prompts/baseline.txt`, `prompts/improved.txt` | Attributed baseline and independently developed focused revision |
| `data/source/`, `data/review/`, `data/frozen/` | Immutable source files, human review, frozen evaluation inputs |
| `artifacts/runs/<run_id>/` | Append-only predictions, errors, metadata, trace links, metrics |
| `artifacts/usage.jsonl` | Usage/cost accounting across pilots, attempts, and experiments |
| `reports/` | Final workbook, evaluation report, trace evidence, demo outline |
| `tests/` | Offline checks of data integrity, scoring, provider failures, and spending safeguards |

Use `FIREWORKS_API_KEY` and `LANGSMITH_API_KEY` in a gitignored local environment. `FIREWORKS_MODEL=accounts/fireworks/models/muse-spark-open`. Configure the actual LangSmith endpoint/workspace for the user's account; do not assume US residency or a default workspace. Proposed project name: `week4-support-muse-spark`.

Use direct LangSmith tracing with LangGraph/model child runs first; OpenTelemetry is unnecessary unless required to resolve a demonstrated integration issue. Store case ID, run ID, prompt version/hash, dataset version/hash, provider/model, expected and predicted category, correctness, concise explanation, latency, token usage, errors, and trace URL. Expected labels belong to evaluation metadata/reference outputs, not model messages. Never serialize credentials into artifacts.

## Metrics and proposed pass bars

These are learning-project targets proposed by the assistant, not agreed production SLAs. Freeze them before the full baseline. A missed target is a valid result, not a reason to change labels or conceal failures.

| Metric | Definition | Proposed target |
|---|---|---|
| Routing accuracy | Correct predictions / all frozen cases, including errored cases in the denominator | At least 95% |
| Macro F1 | Equal-weight F1 over the five routes; invalid/error outputs count as missed true labels | At least 0.90 |
| Valid response rate | Valid category plus explanation / all attempted cases | 100% |
| p95 ticket latency | 95th percentile elapsed seconds for all attempted cases, including failures and any explicit retries | At most 15 seconds |
| Mean inference cost per attempted ticket | All recorded model costs, including failed/retried attempts, divided by attempted cases | At most $0.02 |

Also report per-category precision/recall, confusion matrix with an error/invalid-output column, and counts of wrong→right, right→wrong, unchanged-correct, and unchanged-wrong cases. Cost is an estimate from provider usage and a dated rate card unless reconciled with provider billing. Missing usage means unknown, never zero. Treat unmeasured latency/cost as unavailable.

## Budget and integration pilot

Ramesh has $15 of Fireworks credit and separate LangSmith credit. Proposed project inference allocation: $3, with the remaining credit left available. This is an application guard based on measured/reported usage, not a guarantee of the provider's account-wide balance.

At planning time, the Fireworks model page lists $1.25/M input, $0.15/M cached input, and $4.25/M output tokens. Verify rates and reasoning-token billing before the first paid call. Cached input is a subset of input; do not count it twice. Reconcile reasoning tokens with the provider's total output field rather than adding them twice.

Run a five-ticket integration pilot covering all five categories before full evaluation. Verify serverless access, structured output, output-limit behavior, usage including reasoning, and visible LangSmith parent/child traces. Use sequential calls, disable implicit SDK retries, and propose `max_tokens=1024` initially. Verify that this limit caps all billable generated tokens for this model; if it does not, establish a supported limit before scaling. Record actual model settings and freeze them for both experiments. Do not silently switch models if access fails.

Before each call, reserve a conservative cost bound using the verified output cap and input accounting with margin. Refuse a call when recorded spend plus reservations exceeds $3. If token bounds, pricing, or usage cannot be established, stop additional paid calls for review rather than claiming the budget is enforced. Record pilot costs in the same ledger. Do not issue automatic retries; explicit reruns get new attempt records and retain failed attempts. Never rerun completed paid cells just to recreate reports.

## Experiment procedure

1. Acquire and attribute the source materials, reconcile their versions, and prepare label review.
2. Obtain Ramesh's review and freeze the dataset and metric targets.
3. Verify the five-case pilot, costs, and trace structure, then create the LangSmith dataset.
4. Run a fresh baseline on all frozen cases and save every result, including errors.
5. Review every failure and a sample of passes. Draft evidence-based annotations and cluster actual failures into 2–4 categories where the data supports them. Ramesh reviews the interpretation. Rank by frequency and qualitative downstream cost; do not invent monetary losses.
6. Select one category and write one focused prompt change with a predicted effect. Freeze v2 before rerunning. If there are no substantive failures, report that honestly and review options before expanding the experiment; do not deliberately weaken the model.
7. Rerun all frozen cases under identical model settings. Compare paired cases and inspect wins/regressions in LangSmith. Treat one-run deltas as descriptive evidence subject to model variability.
8. Complete the workbook, report, trace evidence, and demo outline using saved results.

## Deliverables and scope reconciliation

The track handout calls for one focused change; the general handout calls for 3–4 changes and 30–50 examples. Our explicit core scope follows the track's single-change exercise and uses the provided 100-case corpus after review. Record this discrepancy in the report; do not claim all general checklist items are satisfied. The general handout's notebook/tracing and demo requirements are retained. If strict general-rubric compliance is later required, propose separately measured extra changes rather than silently expanding scope.

Deliver a completed workbook with annotations, failure categories, labels, prompt change, and our paired results; an executed notebook; versioned dataset and prompts; LangSmith experiment/trace links or screenshots; a concise report; and a 3–5 minute demo outline. Ramesh records the final narrated demo unless another recording workflow is requested. Optional judge sections are marked not attempted.

## Completion and limits

Complete means the notebook can reproduce analysis from saved artifacts, all included labels are human reviewed, two fresh experiments share the same dataset and model settings, results account for errors and regressions, trace evidence is verified, and submission artifacts are consistent. It does not require hitting quality targets or manufacturing a positive delta.

Non-goals: LLM judges, Jev, fine-tuning, retrieval, a support UI, deployment, real customer integrations, automatic posting/submission, and independent production-reliability claims. Builder discretion covers visualization styling, small internal helpers, and compatible dependency pins; it does not cover routing-policy changes, silently switching models, or exceeding the proposed allocation.

## Sources

- Local `Week 4 Project Handout (Oct 2026).md` and `Customer Support Agent Evaluation Project Handout.md`.
- Starter: https://github.com/The-Gen-Academy/4A-Customer-Support-Agent-Evaluation
- Model and pricing: https://fireworks.ai/models/fireworks/muse-spark-open
- Integration: https://docs.langchain.com/oss/python/integrations/chat/fireworks
- Structured output: https://docs.fireworks.ai/structured-responses/structured-response-formatting
- Evaluation: https://docs.langchain.com/langsmith/evaluation
