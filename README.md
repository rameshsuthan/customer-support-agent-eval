# Customer Support Routing Evaluation

A local evaluation of Meta Muse Spark Open on Fireworks, with LangGraph classification and LangSmith experiments. We review the course tickets, run our own baseline, diagnose failures, and test one focused prompt revision.

## Submission guide

**Customer Support core track.** Start with the [submission Word document](reports/customer_support_submission.docx), which includes diagrams and handout-aligned evidence, or the [solution PDF](reports/customer_support_solution.pdf), then open the [workbook](reports/customer_support_evaluation.xlsx) and [executed notebook](notebooks/customer_support_evaluation.ipynb). Download the workbook to inspect its sheets.

**Demo video:** [Watch or download the narrated MP4](reports/video/customer_support_demo.mp4) (5:01, 1080p, standard synthetic voice, captions included). [Transcript](reports/video/transcript.txt) and [SRT captions](reports/video/customer_support_demo.srt) are also available. This is a presentation-style walkthrough of saved project evidence. Loom hosting is still pending if the submission portal requires a Loom URL. See the [submission checklist](reports/SUBMISSION_CHECKLIST.md).

| Run | Output limit | Accuracy | Valid responses |
|---|---:|---:|---:|
| Original baseline | 1,024 | 91% | 96% |
| Unchanged-prompt control | 2,048 | 96% | 100% |
| Focused priority edit | 2,048 | 98% | 98% |

All runs use the same 100 human-reviewed tickets. The controlled prompt comparison has **four routing fixes and two output-limit regressions**. The prompt gain is 96% to 98%; the full 91% to 98% difference also includes a settings change and run variability.

- **Solution and findings:** [PDF](reports/customer_support_solution.pdf), [detailed report](reports/final_report.md), [failure analysis](reports/failure_analysis.md).
- **Spreadsheet:** the `Our` sheets contain our results. `Our Reviewed Labels` documents the human review; `Our Failure Analysis` covers Steps 1–3; `Our Paired Results` and the prompt files cover Step 4. In `Our Results`, Correct 1 means PASS and 0 means FAIL. Original course tabs are preserved reference material.
- **Reproducibility:** [frozen dataset](data/frozen/v1), [saved results](artifacts/runs), [prompts](prompts), [agent/evaluation code](src/support_eval), and [tests](tests).
- **LangSmith:** [control experiment](https://smith.langchain.com/o/82c36783-971e-46c1-862e-a27d43bbcba3/datasets/892c6169-ac98-4d08-b4be-8363f254cc11/compare?selectedSessions=fbf15121-6924-4b0a-9c37-de46208b0b45), [improved experiment](https://smith.langchain.com/o/82c36783-971e-46c1-862e-a27d43bbcba3/datasets/892c6169-ac98-4d08-b4be-8363f254cc11/compare?selectedSessions=a6ba6566-3751-417b-95cc-0de7e769182f), and [saved inspected trace evidence](reports/trace_evidence). Live links require workspace access.

Known project cost including the pilot: **$0.79069535**, excluding two unknown-cost original requests. Conservative exposure: **$3.42083935** under the approved $5 ceiling. All 42 tests and fresh-kernel analysis replay passed. The notebook's paid flags default to false; saved-results analysis needs no API keys.

AI assistance supported implementation, analysis and documentation. Ramesh reviewed the ground truth and routing policy and approved the experimental design. A synthetically narrated demo video is included. External course submission has not been performed.

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

Core track: one focused prompt change, reviewed supplied cases, fresh baseline/improved results, workbook, notebook, trace evidence, report and demo. Optional LLM judge work is excluded. The general handout's 3–4 changes and 30–50 cases belong to the separate Own Use Case track; this project follows the Customer Support checklist.
