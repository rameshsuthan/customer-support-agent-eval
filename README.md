# Customer Support Routing Evaluation

A local evaluation of Meta Muse Spark Open on Fireworks, with LangGraph classification and LangSmith experiments. We review the course tickets, run our own baseline, diagnose failures, and test one focused prompt revision.

## Current status

The offline dataset, classifier, experiment runner, and scoring tools are implemented. Python 3.12 and dependencies are installed in `.venv`. All 100 labels are reviewed and dataset v1 is frozen. The five-ticket integration pilot completed with five valid/correct responses and estimated inference cost $0.0132835. LangSmith child traces and usage were inspected. Three measured runs are complete on the same 100 reviewed tickets: original 1024-token baseline 91% accuracy; unchanged-prompt2048-token control 96%; focused refund-priority prompt at2048 tokens 98%. The prompt pair has four routing fixes and two output-limit regressions. Valid responses fell from 100% to 98%, so the final version does not meet the 100% validity target.

Deliverables: [final report](reports/final_report.md), [workbook](reports/customer_support_evaluation.xlsx), [notebook](notebooks/customer_support_evaluation.ipynb), and [demo outline](reports/demo_outline.md). The workbook preserves source tabs and adds clearly identified Our sheets. Known project estimate including pilot is $0.79069535, excluding two unknown-cost calls. Conservative exposure is $3.42083935 under the approved $5 ceiling. All 42 offline tests and fresh-kernel analysis replay pass. Ramesh's demo recording and course submission remain pending.

## Start locally

```bash
source .venv/bin/activate
jupyter lab notebooks/customer_support_evaluation.ipynb
```

For a fresh installation with Python 3.12:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-lock.txt
```

The notebook adds `src` to its import path. To use modules from the terminal, set `PYTHONPATH=src`. Run offline checks with `python -m pytest -q` from the project root.

## Configure accounts

Use the gitignored `.env` file, with `.env.example` as the reference. Configure `FIREWORKS_API_KEY`, `LANGSMITH_API_KEY`, the correct LangSmith endpoint, and a workspace ID if your key accesses several workspaces. No OpenAI account is needed. Never paste keys into notebook cells or outputs.

`INTEGRATION_VERIFIED` stays `false` until the pilot confirms model access, structured output, token accounting, output cap, current rates and visible LangSmith traces. Full client-backed runs refuse to proceed while it is false. Paid notebook cells are also switched off by default.

## Review ground truth

Read [the review guide](reports/label_review_guide.md) and [routing decisions](reports/label_policy.md). Edit `data/review/label_review.csv`:

- `suggested_label` is an assistant proposal, not human approval.
- Fill `reviewed_label` and set `review_status=approved` after reviewing that ticket.
- For a correction, explain the decision in `review_note`.
- For an unresolved case, use `review_status=excluded` and explain why.
- Preserve original ticket text and original labels.

The freeze operation rejects pending reviews, invalid labels, duplicate IDs, unexplained exclusions and overwrites. It saves a review snapshot and a checksum. Editing a frozen dataset is detected; intentional changes require a new version and new baseline/improved runs.

## What the source inspection found

The supplied workbook has 150 tickets and 29 failures. The repository CSV has 100 tickets and 8 supplied baseline failures. Only one of the 100 shared IDs has identical ticket text, and some identical texts have conflicting labels. These are different teaching artifacts. See [source reconciliation](reports/source_reconciliation.md).

We use the CSV's fixed texts as our candidate dataset; all labels were human reviewed before freezing. The supplied predictions and 92%→97% scores are reference material, never our measured results. Cases are synthetic and related by seed families. Results on the same cases used for diagnosis do not demonstrate held-out generalization.

## Paid-run safeguards and limits

- Approved Fireworks ceiling: **$5** (raised from $3 after two unknown-usage HTTP 500 failures) of the user's $15 credit. LangSmith billing is separate.
- Sequential calls and no automatic SDK retries.
- A project-wide lock prevents simultaneous runner instances. Each attempted call reserves budget before sending and records usage afterward.
- Reservations conservatively use the model's entire input context plus the configured output cap; a pending/unpriced attempt blocks later calls until reviewed. An explicit `bounded_unknown` ledger event can retain the full original reservation as conservative budget exposure while leaving actual cost unknown.
- Actual cost estimates use the saved price snapshot and reported usage, avoiding cache/reasoning double counting. They are not provider invoices or an account-wide spend limit.
- Completed run IDs cannot be reused. Explicit `resume=True` accepts only an identical incomplete run specification, checks saved results against the usage ledger, and calls only unattempted cases. Prior errors remain scored failures. Continuations use separate LangSmith experiments; local combined results define full-run metrics.
- Analysis cells read saved files and never call the model. Full metrics require all expected cases and validate result identity against the run specification.

The pilot must verify current model cap/billing behavior before scaling. No result is represented as correct merely because a provider call failed, and costs with missing usage are not reported as zero.

## Artifacts and ownership

- `data/source/`: unchanged course references and pinned source manifest.
- `data/review/`: human decisions, separate from original labels.
- `data/frozen/`: appears after review and explicit freezing.
- `prompts/baseline.txt`: simple category descriptions adapted with attribution; `prompts/improved.txt` adds the reviewed priority rule.
- `artifacts/runs/`: our newly measured results only.
- `reports/`: policy, source evidence, review guide, and eventually final submission.

The reference files come from [The Gen Academy](https://github.com/The-Gen-Academy/4A-Customer-Support-Agent-Evaluation), revision `ef517b274cf86a2c4fa8ae72fdc89b3dce80f41d`. No source license was found through GitHub's license endpoint; reference materials are retained for this local course exercise, without assuming redistribution permission. The Python implementation is independently written.

## Submission scope

Core track: one focused prompt change, reviewed supplied cases, fresh baseline/improved results, workbook, notebook, trace evidence, report and demo. Optional LLM judge work is excluded. The track-specific scope differs from the general handout's 3–4 changes and 30–50 cases; disclose that difference rather than claiming every general-rubric item is satisfied.
