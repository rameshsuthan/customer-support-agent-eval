# Customer Support submission checklist

The repository is the submission package. No ZIP is needed. Requirements are taken from the Customer Support checklist and Final submission section of the Week 4 handout, plus the track handout's Steps 1–4.

| Requirement | Repository evidence | Status |
|---|---|---|
| Completed spreadsheet | [Workbook](customer_support_evaluation.xlsx) | Ready |
| Reviewed/corrected labels | Our Reviewed Labels; `data/frozen/v1/review_snapshot.csv` | 100 reviewed |
| Predictions and PASS/FAIL | Our Results: Correct 1 = PASS, 0 = FAIL; statuses retain invalid/provider failures | 300 scored results |
| Step 1 annotations and Steps 2–3 failure groups/labels | Our Failure Analysis; [detailed analysis](failure_analysis.md) | Ready |
| Step 4 prompt change and comparison | Our Paired Results; `prompts/improved.txt`; solution PDF | Ready |
| Solution document | [Solution PDF](customer_support_solution.pdf) and [detailed report](final_report.md) | Ready |
| Executed notebook | [Notebook](../notebooks/customer_support_evaluation.ipynb) | Outputs saved; paid flags off |
| LangSmith evidence | Links in the solution/report; `trace_evidence/`; each result row has a trace URL | Saved evidence ready; check reviewer access |
| Short Loom | [Demo script](DEMO_SCRIPT.md) | Ramesh to record and add link |
| Optional LLM-as-a-Judge | Not attempted | Not required for this core-track submission |

## Before sharing the repository

- [ ] Record the 3–5 minute Loom using the demo script.
- [ ] Put the Loom link near the top of the repository README and in the portal submission.
- [ ] Confirm that the repository link opens for the instructor. For a private repository, grant the required access.
- [ ] Check instructor access to LangSmith links. If access is unavailable, include screenshots of the t044 fix and t083 regression, showing the ticket ID, input/output, model child and metadata. Saved JSON evidence is already included; do not claim private links are public.
- [ ] Confirm the portal accepts a repository link; upload the workbook, PDF and notebook separately if it requires file attachments.
- [ ] Open the pushed branch's README, PDF, workbook download and notebook preview once before submitting.

## What to say about scope

This is the Customer Support Agent Evaluation core track: one focused prompt change on 100 reviewed supplied tickets, plus an approved output-limit control. The 30–50 cases and 3–4 changes in the general handout belong to the separate Own Use Case track. LLM-as-a-Judge is optional and was not attempted.

## What not to claim

- Do not say the prompt alone caused the entire 91% to 98% increase. Its controlled comparison is 96% to 98%.
- Do not say there were no regressions. There were four fixes and two output-limit regressions.
- Do not call $0.791 a complete invoice total. It excludes two requests with unknown usage.
- Do not claim production readiness or held-out generalization from these synthetic diagnosis cases.
- Do not claim a Loom recording or submission is complete until you have actually done it.
