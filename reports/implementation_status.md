# Implementation checkpoint — November 2, 2026

## Implemented and verified

- Python 3.12 `.venv`, installed dependencies and exact lock file.
- Source files pinned to a GitHub revision and checked with SHA-256 hashes.
- Workbook/CSV reconciliation: 150 vs 100 cases; 29 vs 8 supplied failures; only one matching ticket among 100 shared IDs.
- Independent dataset-review/freezing code, Fireworks/LangGraph classifier, experiment runner, usage ledger, and scoring/comparison tools.
- 34 passing offline tests, including source-label integrity, missing-case scoring, cross-run identity and an unverified-integration gate.
- Notebook executed in a fresh kernel with all paid switches off.
- Both service credentials configured locally; values never included in output or Git.

## Human review

- course-t004–t007: Ramesh selected `refund_request`, changing the source labels.
- course-t044–t047: Ramesh retained `product_issue`.
- **8/100 reviewed; 92 pending.** No dataset is frozen and no case has been silently approved.
- Next walkthrough: course-t068–t071, session/logout failures during checkout.

## Pending

- Remaining human label review and frozen dataset.
- Five-case paid pilot: model access, structured output, billing/cap semantics and trace visibility.
- Full baseline, reviewed failure analysis, one independently developed prompt improvement and full rerun.
- Final workbook, measured report, trace evidence and narrated demo. Do not treat the current notebook as an executed evaluation submission.

## Decisions and review record

- Initialized a project branch in the new local folder rather than a linked worktree; there was no existing repository/branch to isolate.
- Continued independent offline implementation while human review and live prerequisites remained pending; this does not waive either gate.
- Budget reserves the entire model input context at uncached pricing plus capped generation. This is deliberately conservative and may stop earlier than the nominal $3 allocation. Rates and cap behavior still need live verification.
- Code review found three material gaps: missing cases could inflate standalone scores; comparison did not bind results to reference identities; the full-run integration gate was not enforced. Each was reproduced in a failing test and fixed. The entire suite then passed 34 tests.
- A reviewer noted a minor limitation: whitespace-only explanations pass the present minimum-length validator. Deferred; category correctness is still checked, but the explanation-quality check could be tightened later.
- Live model access, billing semantics, trace visibility and human labels were not judged by the code reviewer because those require external evidence. They remain pending prerequisites, not assumed successes.

No Fireworks inference calls have been made by this implementation checkpoint. LangSmith experiment creation and upload have not started.
