# Customer Support Routing Evaluation

A local evaluation of Meta Muse Spark Open on Fireworks, with LangGraph classification and LangSmith experiments. We review the course tickets, run our own baseline, diagnose failures, and test one focused prompt revision.

## Current status

The offline dataset, classifier, experiment runner, and scoring tools are implemented. Python 3.12 and dependencies are installed in `.venv`. **No paid runs or measured project results exist yet.** Human review is in progress; inspect the CSV for the current count. The integration pilot, full baseline, improvement experiment, final workbook and demo remain pending.

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

We use the CSV's fixed texts as our candidate dataset; all labels remain subject to human review. The supplied predictions and 92%→97% scores are reference material, never our measured results. Cases are synthetic and related by seed families. Results on the same cases used for diagnosis do not demonstrate held-out generalization.

## Paid-run safeguards and limits

- Proposed Fireworks allocation: **$3** of the user's $15 credit. LangSmith billing is separate.
- Sequential calls and no automatic SDK retries.
- A project-wide lock prevents simultaneous runner instances. Each attempted call reserves budget before sending and records usage afterward.
- Reservations conservatively use the model's entire input context plus the configured output cap; a pending/unpriced attempt blocks later calls until billing is reconciled.
- Actual cost estimates use the saved price snapshot and reported usage, avoiding cache/reasoning double counting. They are not provider invoices or an account-wide spend limit.
- An existing run ID cannot be reused. Interrupted runs remain incomplete; recovery is explicit.
- Analysis cells read saved files and never call the model. Full metrics require all expected cases and validate result identity against the run specification.

The pilot must verify current model cap/billing behavior before scaling. No result is represented as correct merely because a provider call failed, and costs with missing usage are not reported as zero.

## Artifacts and ownership

- `data/source/`: unchanged course references and pinned source manifest.
- `data/review/`: human decisions, separate from original labels.
- `data/frozen/`: appears after review and explicit freezing.
- `prompts/baseline.txt`: simple category descriptions adapted with attribution; improved prompt comes after our baseline analysis.
- `artifacts/runs/`: our newly measured results only.
- `reports/`: policy, source evidence, review guide, and eventually final submission.

The reference files come from [The Gen Academy](https://github.com/The-Gen-Academy/4A-Customer-Support-Agent-Evaluation), revision `ef517b274cf86a2c4fa8ae72fdc89b3dce80f41d`. No source license was found through GitHub's license endpoint; reference materials are retained for this local course exercise, without assuming redistribution permission. The Python implementation is independently written.

## Submission scope

Core track: one focused prompt change, reviewed supplied cases, fresh baseline/improved results, workbook, notebook, trace evidence, report and demo. Optional LLM judge work is excluded. The track-specific scope differs from the general handout's 3–4 changes and 30–50 cases; disclose that difference rather than claiming every general-rubric item is satisfied.
