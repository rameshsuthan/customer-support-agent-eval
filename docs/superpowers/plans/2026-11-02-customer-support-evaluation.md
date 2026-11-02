# Customer Support Routing Evaluation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task in the current session. Steps use checkbox (`- [ ]`) syntax for tracking. This is the proposed execution method; implementation has not started.

**Goal:** Produce an original, reproducible evaluation of Muse Spark Open ticket routing, with human-reviewed labels, one focused prompt improvement, and measured results linked to LangSmith traces.

**Architecture:** Run a small single-node LangGraph classifier from a local Jupyter notebook using Fireworks. Keep dataset handling and experiment/scoring logic in small Python modules; preserve immutable inputs and append-only run artifacts. LangSmith stores the frozen dataset and paired experiments; the workbook and report are generated from saved results.

**Tech Stack:** Python 3.11 or 3.12, JupyterLab, LangGraph, langchain-fireworks, LangSmith, Pydantic, pandas, scikit-learn, openpyxl, python-dotenv, pytest.

**Spec:** [Customer Support Routing Evaluation — Design](../specs/2026-11-02-customer-support-evaluation-design.md)

## Global Constraints

- Agreed choices: Customer Support core track; local execution; Fireworks AI with Muse Spark Open; a separate LangSmith account; no optional LLM judge.
- `FIREWORKS_MODEL=accounts/fireworks/models/muse-spark-open`.
- Proposed project name: `week4-support-muse-spark`.
- Proposed project inference allocation: $3, with the remaining credit left available.
- Use sequential calls, disable implicit SDK retries, and propose `max_tokens=1024` initially.
- Expected labels belong to evaluation metadata/reference outputs, not model messages.
- Both are scored against the same documented policy.
- Missing usage means unknown, never zero.
- Changing a label requires a new dataset version and rerunning both experiments.
- Do not silently switch models if access fails.
- No credentials, implementation, dependencies, Git repository, or paid calls are created by preparing this plan.

## Review Focus

- Identical-looking IDs from different source artifacts: reject silent joins when ticket texts differ; Task 1.
- Plausible but unapproved labels: block freezing and model evaluation until included labels are reviewed; Task 1.
- Invalid outputs, timeouts, or absent usage: preserve attempts and treat them as failures/unknown costs; Tasks 2–3.
- Notebook reexecution: load saved artifacts by default and refuse to overwrite/reissue a completed run; Task 3.
- Apparent improvement caused by dataset/model changes or missing cases: refuse comparison; Task 4.

## File responsibilities

| Files | Responsibility |
|---|---|
| `README.md`, `.gitignore`, `.env.example`, `requirements.txt`, `requirements-lock.txt` | Setup, attribution, safe local configuration, reproducible packages |
| `src/support_eval/{__init__,config,dataset,agent,evaluation}.py` | Reusable configuration, data, classification, execution and analysis |
| `notebooks/customer_support_evaluation.ipynb` | Learning narrative and explicit execution cells |
| `prompts/{baseline,improved}.txt` | Versioned baseline and one independently developed prompt change |
| `data/source/manifest.json`, source CSV/XLSX | Download origins, source revision, hashes, unchanged source files |
| `data/review/label_review.csv`, `data/frozen/tickets_v1.jsonl`, `data/frozen/manifest.json` | Human review and frozen dataset |
| `artifacts/runs/<run_id>/{manifest.json,results.jsonl,metrics.json}`, `artifacts/usage.jsonl` | Attempt records, experiment links, scores and cost accounting |
| `reports/{source_reconciliation,label_policy,failure_analysis,final_report,demo_outline}.md` | Written evidence and final story |
| `reports/customer_support_evaluation.xlsx`, `reports/trace_evidence/` | Course workbook with fresh results and trace evidence |
| `tests/test_{dataset,agent,runner,metrics}.py` | Meaningful offline integrity and evaluation checks |

## Task 1: Reconcile source data and prepare the human review

**Files:** Setup files, `src/support_eval/dataset.py`, source/review/frozen data paths, `reports/source_reconciliation.md`, `reports/label_policy.md`, `tests/test_dataset.py`.

**Interfaces:**
- `load_source_cases(csv_path: Path) -> pd.DataFrame`: returns source ID, ticket text, original label, source file.
- `make_review_table(cases: pd.DataFrame) -> pd.DataFrame`: adds stable case IDs, reviewed label, review status and note; does not approve labels.
- `freeze_dataset(review: pd.DataFrame, output_dir: Path, version: str) -> dict`: validates and writes sorted frozen JSONL plus manifest, returning the manifest.
- Frozen rows: `case_id`, `ticket_text`, `expected_category`, `source_case_id`, `source_file`; manifest: version, SHA-256, case count, category counts, exclusions and provenance.

- [ ] Inspect local Python and Git status without reading credential values. Create an isolated `.venv` at implementation time, choose a compatible interpreter, and document the choice.
- [ ] Create setup files and ignore `.env`, `.venv`, notebook checkpoints, and accidental key files. Keep `.env.example` as placeholders only. Install necessary packages and record resolved versions after the integration checks.
- [ ] Fetch the pinned source revision, notebook, CSVs, and workbook; preserve bytes and record hashes. Inspect licensing and mark any reused portions. Do not import source outputs as our experiment results.
- [ ] Inspect CSV/workbook ticket identities and explain the 29-vs-8 failure discrepancy as far as the evidence supports. Record unresolved source differences explicitly.
- [ ] Write `test_freeze_rejects_pending_labels`, `test_duplicate_id_conflict_rejected`, `test_invalid_category_rejected`, and `test_changed_text_changes_hash`. Each asserts the named invalid state raises `ValueError` or changes the manifest hash as appropriate; reordering approved rows must not change the hash.
- [ ] Run `python -m pytest tests/test_dataset.py -q`; confirm the tests fail before the missing behavior is implemented.
- [ ] Implement source import, review table, category validation, exclusion accounting, and stable freeze/hash behavior. Store original and reviewed labels separately.
- [ ] Run `python -m pytest tests/test_dataset.py -q`; require all tests to pass.
- [ ] Present the review table to Ramesh. Write routing-policy rationale and assistant-suggested corrections as proposals; obtain human review of every included label before freezing. Independent implementation tasks may proceed while review is pending.
- [ ] Freeze approved cases as `tickets_v1`; record the actual count rather than assuming all 100 survive review. Confirm that baseline and improved runs will load this exact file.

**Checkpoint:** A traceable candidate corpus and human-approved frozen dataset. No model-generated labels are represented as human decisions. Initialize/use local Git at implementation time and commit this coherent setup/data work if repository permissions permit; otherwise report the limitation without blocking data preparation.

## Task 2: Build the Fireworks classifier and verify one integration pilot

**Files:** `config.py`, `agent.py`, `prompts/baseline.txt`, `tests/test_agent.py`, notebook setup/pilot sections, `requirements-lock.txt`.

**Interfaces:**
- `Settings`: Fireworks key/model, LangSmith key/endpoint/workspace/project, proposed budget 3.0 USD, initial output limit 1024, model sampling settings; secret fields excluded from repr/serialization.
- `load_settings() -> Settings`: validates configuration without printing keys.
- `Prediction`: Pydantic model with exactly one allowed `category` and nonempty concise `explanation`.
- `build_agent(settings: Settings, prompt: str) -> CompiledStateGraph`: consumes `{"ticket_text": str}`, returns prediction and provider usage/raw response metadata; does not accept expected labels.
- Model factory is injectable for offline tests; tests never require API credentials.

- [ ] Write `test_agent_accepts_five_categories`, `test_agent_rejects_invalid_category`, `test_reference_labels_never_enter_messages`, and `test_provider_failure_is_not_other`. Use a fake model to capture messages and inject invalid/failed responses; failures must propagate for Task 3 to record.
- [ ] Run `python -m pytest tests/test_agent.py -q`; confirm missing behavior fails.
- [ ] Implement settings loading and the single-node classifier using `ChatFireworks`, retaining raw usage with the parsed prediction. Use provider-supported structured output; validate the actual Muse Spark integration rather than assuming all Fireworks models behave identically.
- [ ] Save an attributed baseline using the starter's simple category descriptions and a structured-output instruction; leave policy-disambiguation improvements for Task 5. Record this adaptation explicitly.
- [ ] Run `python -m pytest tests/test_agent.py -q`; require all tests to pass.
- [ ] Add notebook instructions to configure keys locally and choose the correct LangSmith endpoint/workspace. Stop live work if credentials are absent; continue offline work without requesting keys in chat.
- [ ] After Task 3's accounting/runner exists and Task 1 labels are frozen, execute five pilot cases across all routes. Verify valid predictions, complete usage, serverless access, and visible parent/child traces in the selected LangSmith workspace.
- [ ] Check the current rate card, cached/reasoning token accounting, and supported generation cap. Save the validated configuration and price timestamp. If the pilot requires a setting change, record its costs and freeze the final settings before either full experiment.
- [ ] Record compatible dependencies in `requirements-lock.txt`; preserve pilot trace links and measured cost.

**Checkpoint:** One inspected LangSmith trace and five accounted-for pilot attempts. The implementation is reusable with our dataset and does not silently replace the user's model.

## Task 3: Run bounded experiments and retain every attempt

**Files:** `evaluation.py`, `tests/test_runner.py`, notebook execution sections, run artifacts and usage ledger.

**Interfaces:**
- `RunSpec`: run ID, prompt version/hash, dataset version/hash, model/settings fingerprint, price snapshot, and LangSmith dataset/experiment identifiers.
- `ResultRow`: case/run IDs, expected category, nullable predicted category/explanation, status (`ok`, `invalid`, `error`), correctness, elapsed seconds, nullable usage/cost, error text, trace URL and attempt number.
- `ensure_langsmith_dataset(cases: pd.DataFrame, manifest: dict, client: Client) -> str`: idempotently creates/resolves the versioned dataset; verifies content before reuse.
- `run_experiment(agent, cases: pd.DataFrame, run_spec: RunSpec, settings: Settings, output_dir: Path) -> pd.DataFrame`: executes sequentially and persists each result before continuing.
- `can_start_call(recorded_usd: float, reserved_usd: float, next_bound_usd: float, budget_usd: float) -> bool`.

- [ ] Write tests for provider exception retention, timeout retention, missing usage halting additional calls, completed-run reuse refusal, and interrupted-run artifact preservation. Stub the provider and LangSmith client.
- [ ] Add budget boundary assertions: `can_start_call(2.90, 0, 0.10, 3.0)` is true, while `can_start_call(2.90, 0, 0.11, 3.0)` is false. Test decimal-safe accounting and that cached/reasoning tokens are not double-counted.
- [ ] Run `python -m pytest tests/test_runner.py -q`; confirm missing behavior fails.
- [ ] Implement conservative pre-call reservations using verified token bounds and the price snapshot; include pilot and failed-attempt costs. If a trustworthy bound cannot be obtained, block scaling beyond the pilot and surface what needs review.
- [ ] Implement explicit, sequential execution with hidden retries disabled; timestamp each attempt and capture errors as result rows, never as a valid `other` prediction. Unknown usage stops subsequent calls and retains the attempted row.
- [ ] Create/verify the LangSmith dataset and use the SDK's documented dataset experiment API with concurrency one. Wrap each example in the same ticket-level trace structure for both versions, with the model call nested beneath it. Return an error status from caught per-case exceptions so they remain visible in experiment results.
- [ ] Save run configuration and dataset identity before model calls, then append results and ledger entries after each attempt. Refuse an existing run ID; notebook report cells read artifacts and never trigger inference. Interrupted runs remain incomplete; resumption is an explicit later operation, not an automatic retry.
- [ ] Run `python -m pytest tests/test_runner.py -q`; require all tests to pass. Complete the Task 2 pilot before allowing full experiments.

**Checkpoint:** Every attempted ticket has a durable local record and trace metadata, with verified spend accounting and no automatic repeated calls. Commit the classifier/runner integration together after its offline checks and pilot verification.

## Task 4: Score results and make trustworthy paired comparisons

**Files:** `evaluation.py`, `tests/test_metrics.py`, notebook analysis sections.

**Interfaces:**
- `score_results(results: pd.DataFrame, run_spec: RunSpec) -> dict`: five headline metrics plus per-class metrics, error-aware confusion matrix, cost coverage, and error counts.
- `compare_runs(baseline: pd.DataFrame, improved: pd.DataFrame, baseline_spec: RunSpec, improved_spec: RunSpec) -> pd.DataFrame`: exact case/text/label matching and model/settings validation, then win/regression/unchanged classification.

- [ ] Write `test_error_counts_in_accuracy_denominator`: four cases with two correct, one wrong and one error yield accuracy `0.5` and valid-response rate `0.75`.
- [ ] Write `test_errors_reduce_true_class_recall`, `test_paired_counts_include_regressions`, `test_mismatched_dataset_or_model_rejected`, and `test_missing_case_rejected`. Include reordered result rows to prove matching is by ID rather than position.
- [ ] Write `test_unknown_cost_is_not_zero`: missing usage makes aggregate cost incomplete, with explicit coverage, not an underestimated complete total. Latency retains errored cases.
- [ ] Run `python -m pytest tests/test_metrics.py -q`; confirm missing behavior fails.
- [ ] Implement metrics over all expected frozen cases, five-class macro F1, and an error column in the confusion matrix. Use a documented NumPy/pandas percentile convention. Reject headline comparisons of incomplete runs.
- [ ] Implement paired comparisons and metric deltas with dataset/policy/model/settings identity checks. Prompt hash is expected to differ; dataset and model fingerprints must not.
- [ ] Run `python -m pytest tests/test_metrics.py -q`; require all tests to pass. Add readable tables/plots using saved fixtures and no paid calls.

**Checkpoint:** A known fixture proves scores cannot improve merely by dropping failed cases or changing the corpus. Commit the scoring/analysis work.

## Task 5: Conduct the original baseline, analysis, and prompt experiment

**Files:** Completed notebook, `prompts/improved.txt`, `reports/failure_analysis.md`, two run directories.

**Consumes:** Frozen cases, validated agent/pilot, bounded runner, metrics and comparison interfaces from Tasks 1–4.
**Produces:** Fresh baseline and improved experiment artifacts plus a documented, human-reviewed causal hypothesis.

- [ ] Record the proposed pass bars before the full baseline: accuracy ≥95%, macro F1 ≥0.90, valid responses 100%, p95 ≤15 seconds, mean inference cost ≤$0.02/attempted ticket. Describe them as project targets rather than production claims.
- [ ] Run the baseline on every frozen case using the locked configuration; verify completeness, scores, total usage and trace links.
- [ ] Draft annotations for every failed ticket and inspect a sample of passes. Distinguish policy/label ambiguity, classifier error, and infrastructure error. Obtain Ramesh's review of the substantive analysis.
- [ ] Group supported patterns into 2–4 categories where possible, with definitions, counts, representative cases, and qualitative downstream cost. Do not force nonexistent clusters or claim invented loss figures.
- [ ] Select one substantive category and record one focused prompt edit, the targeted boundary, expected benefit, and plausible regression. Write `improved.txt` independently of the source solution.
- [ ] If labels need correction, freeze a new dataset and rerun both experiments; do not compare against the old baseline. If no substantive failures exist, report this and discuss scope before extra generation or model changes.
- [ ] Run the improved prompt on all the same cases with identical model/settings. Save every output and inspect representative fixes, remaining failures, and regressions in LangSmith.
- [ ] Produce paired metric deltas and state whether targets and the hypothesis were met. A negative or zero improvement is an acceptable measured outcome; do not select only favorable generations.

**Checkpoint:** The original evidence is complete and traceable. Record that evaluating the same diagnosis set measures exercise-set improvement, not independent generalization. Commit prompts and measured artifacts after checking for credentials.

## Task 6: Assemble and verify the submission

**Files:** Final workbook, report, executed notebook, trace evidence and demo outline in `reports/`.

**Consumes:** Saved source/review/frozen data and both experiments; no new model calls required.
**Produces:** Reviewable course submission artifacts, with optional judge work marked not attempted.

- [ ] Read the spreadsheet skill when implementing XLSX work. Preserve original source tabs and values; add clearly identified sheets for our reviewed labels, fresh baseline results, annotations, failure categories, prompt change, and paired comparison. Explain differences from any prefilled 29-failure exercise.
- [ ] Verify workbook totals and formulas against the CSV/JSON metrics and visually inspect the rendered workbook using the spreadsheet skill workflow. Do not create tests solely for cosmetic formatting.
- [ ] Write the report with the evaluation one-liner, routing policy, provenance, metrics/targets, actual baseline and improved results, costs, regression examples, limitations, attribution, and next steps. Explicitly state the single-change/100-case scope differs from the general rubric's 3–4-change/30–50-case wording.
- [ ] Add verified LangSmith experiment links and at least one illustrative trace screenshot or link. Do not claim child-run visibility without inspecting it.
- [ ] Finalize the notebook with retained paid-run outputs and replayable analysis. Use a fresh kernel to verify loading artifacts and recomputing reports; live inference cells remain explicitly opt-in and must not rerun during this check.
- [ ] Run `python -m pytest tests -q`; require all offline integrity and scoring checks to pass. Check dataset hashes, case counts, prompt versions, usage coverage, and report/workbook agreement once after final edits.
- [ ] Create a 3–5 minute demo outline: user outcome → routing policy/dataset → baseline failure → prompt change → paired results/traces → limitations. Ramesh records the narration; retain a checklist entry for the recording rather than claiming it exists.
- [ ] Provide local artifact links and remaining limitations. Do not upload a submission or publish externally without a user request. Commit final reviewable artifacts if local Git is available.

## Definition of done

- [ ] Every scored case has a reviewed label and traceable source.
- [ ] Baseline and improved results are newly measured on the same frozen cases/model settings.
- [ ] One original prompt change has an evidence-based hypothesis and a measured delta.
- [ ] Errors, regressions, cost coverage, synthetic-data limits, and scope differences are disclosed.
- [ ] Workbook, report, notebook, and LangSmith evidence agree.
- [ ] Offline checks pass; replaying analysis does not spend additional credit.
- [ ] Demo outline is ready; final recording is explicitly tracked as Ramesh's remaining submission action until recorded.

## Execution handoff

Recommended: implement inline in this session using `superpowers:executing-plans`. The small modules and notebook depend closely on the same dataset and result schema, so sequential implementation makes review and learning easier. Human label review and interpretation remain explicit collaboration steps. Model keys are configured locally when the pilot is ready. No implementation begins as part of this planning request.

## Implementation checkpoint — November 2

Environment, source reconciliation, review table, classifier, runner, scoring and notebook are implemented offline. 34 tests pass. All 100 case labels are human reviewed; dataset v1 is frozen. The live pilot passed; baseline stopped at a provider HTTP 500 after 9 attempts. Usage reconciliation, baseline completion, failure analysis, improved run and final submission remain pending. See `reports/implementation_status.md`.
