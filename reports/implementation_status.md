# Implementation checkpoint — November 2, 2026

## Implemented and verified

- Python 3.12 `.venv`, installed dependencies and exact lock file.
- Source files pinned to a GitHub revision and checked with SHA-256 hashes.
- Workbook/CSV reconciliation: 150 vs 100 cases; 29 vs 8 supplied failures; only one matching ticket among 100 shared IDs.
- Independent dataset-review/freezing code, Fireworks/LangGraph classifier, experiment runner, usage ledger, and scoring/comparison tools.
- 41 passing offline tests, including source-label integrity, missing-case scoring, cross-run identity and an unverified-integration gate.
- Notebook executed in a fresh kernel with all paid switches off.
- Both service credentials configured locally; values never included in output or Git.

## Human review

- course-t004–t007: Ramesh selected `refund_request`, changing the source labels.
- course-t044–t047: Ramesh retained `product_issue`.
- **100/100 reviewed; none pending.** Dataset v1 is frozen with all human approvals preserved in its review snapshot.
- course-t068–t071: Ramesh approved `account_help` for checkout/logout failures.
- course-t056–t059: Ramesh approved `product_issue` with `damaged_packaging` and `missing_manual` tags.
- course-t052–t055: Ramesh approved `product_issue` with `description_mismatch`.
- course-t024–t027: Ramesh approved `refund_request` with `refund_status`.
- course-t032–t035: Ramesh approved `refund_request` with `overcharge`.
- course-t036–t039: Ramesh approved `refund_request` with `refund_method_preference`.
- course-t016–t019: Ramesh approved `order_status` with `tracking_link_failure`.
- course-t076–t079: Ramesh approved `account_help` with `account_security_concern`.
- course-t008–t011: Ramesh approved `order_status` with `delivered_not_received`.
- course-t012–t015: Ramesh approved `order_status` with `delivery_delay`.
- course-t000–t003: Ramesh approved `order_status` with `tracking_not_updated`.
- course-t020–t023: Ramesh approved `refund_request` with `return_for_refund`.
- Review preference: batches of 10 with a proposed label and tag for each ticket.

## Pending

- Baseline `baseline-001` is complete: 100 unique cases, 91% accuracy, 0.927 macro F1, 96% valid responses. Two unknown-cost HTTP 500 failures remain in results; both full reservations count toward the user-approved $5 ceiling.
- Completed pilot `pilot-001`: 5/5 valid and correct, estimated cost $0.0132835; nested model trace verified.
- Human review of the completed failure analysis, followed by the proposed focused prompt change and full rerun.
- Final workbook, measured report, trace evidence and narrated demo. Do not treat the current notebook as an executed evaluation submission.

## Decisions and review record

- Initialized a project branch in the new local folder rather than a linked worktree; there was no existing repository/branch to isolate.
- Continued independent offline implementation while human review and live prerequisites remained pending; this does not waive either gate.
- Budget reserves the entire model input context at uncached pricing plus capped generation. This is deliberately conservative and may stop earlier than the nominal $3 allocation. Rates and cap behavior still need live verification.
- Code review found three material gaps: missing cases could inflate standalone scores; comparison did not bind results to reference identities; the full-run integration gate was not enforced. Each was reproduced in a failing test and fixed. The entire suite then passed 34 tests.
- A reviewer noted a minor limitation: whitespace-only explanations pass the present minimum-length validator. Deferred; category correctness is still checked, but the explanation-quality check could be tightened later.
- Live model access, billing semantics, trace visibility and human labels were not judged by the code reviewer because those require external evidence. They remain pending prerequisites, not assumed successes.

The five-case pilot is complete. The reviewed dataset was uploaded to LangSmith and the 100-case baseline is incomplete. No improved run has been started.

Latest approved batch: t028–t031 (`refund_request`, `cancellation_refund`); t040–t043 (`product_issue`, `damaged_item`); t048–t049 (`product_issue`, `wrong_item_size`).

Approved batch: t050–t051 (`product_issue`, `wrong_item_size`); t060–t063 (`account_help`, `login_failure`); t064–t067 (`account_help`, `payment_method_update`).

Approved batch: t072–t075 (`account_help`, `address_update`); t080–t083 (`other`, `shipping_policy_inquiry`); t084–t085 (`other`, `positive_feedback`).

Approved batch: t086–t087 (`other`, `positive_feedback`); t088–t091 (`other`, `stock_availability`); t092–t095 (`other`, `discount_inquiry`).

Final review batch: t096–t099 approved as `other` / `sale_inquiry`. Frozen dataset: `data/frozen/v1`, 100 cases; SHA-256 `6393654a0bbfb44b3d28dffac7f720c8e857f480dd1480fca4d27cbdbf0efe1d`. Counts: refund_request 24, product_issue 20, account_help 20, other 20, order_status 16. Four source-label corrections: t004–t007 → refund_request. Fireworks model-list read succeeded and includes Muse Spark Open; LangSmith read-access authentication failed.

Provider setup resolution: optional LANGSMITH_WORKSPACE_ID contained a non-UUID value. Omitting it successfully authenticated to the key’s default workspace, so the optional field was cleared. Configuration now validates nonempty workspace IDs as UUIDs; regression test failed before the fix and the complete 35-test suite passes.

Baseline interruption: course-t026 returned Fireworks HTTP 500 in 0.659 seconds with no usage. 91 cases were not attempted. Known estimated cost across the pilot and successful baseline calls: $0.03089405; this excludes unknown cost for the failed request and is not a complete billed total. No full-baseline accuracy is reported. Official Fireworks usage documentation notes delayed aggregation, so an immediate dashboard total would not establish that the failed call was free.

Latest checkpoint: baseline recovered through two separate LangSmith continuation experiments without repeating any attempted case. Known project cost estimate $0.25263815, excluding two unknown-cost requests. Conservative ledger exposure $2.88278215. All100 cases validated against frozen references;41 offline tests pass. Historical interruption notes above are retained as chronology. No inference session remains active.
