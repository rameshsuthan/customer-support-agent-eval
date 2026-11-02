# Demo outline — 3–5 minutes

Recording remains Ramesh's submission action. All scores below are our measured results.

1. **0:00–0:40 — Goal and policy.** Route e-commerce tickets into five support categories. Explain damaged product + refund → product_issue, while non-delivery + refund → refund_request.
2. **0:40–1:15 — Data review.** Show the 100-ticket frozen dataset, descriptive tags and the four human label corrections. Note that the source workbook contains different ticket texts, so its scores were not copied.
3. **1:15–2:00 — Original failures.** Show 91% accuracy: four refund-priority errors, one packaging/manual error, two truncated responses and two HTTP500s. Open a damaged-laptop trace.
4. **2:00–2:40 — Controlled design.** Explain the approved 1024→2048 limit control, which scored 96% with 100% valid responses. Then show the single refund-priority paragraph added at the same 2048 limit.
5. **2:40–3:40 — Paired results.** Open Our Summary and Our Paired Results in the workbook. Prompt edit: 96%→98% accuracy, four fixes, two regressions. Show t044's product_issue prediction and t083's output-limit trace. Both regressions reached 2048 tokens; the edit did not solve response reliability.
6. **3:40–4:30 — Cost, latency and limits.** Control/improved p95: 11.65/13.21 seconds. Known project estimate including pilot: $0.79069535, excluding two unknown-cost calls; conservative exposure $3.42083935 within the $5 ceiling. These are 100 synthetic diagnosis cases, not independent held-out evidence. Optional LLM judge work was not attempted.

Before recording: open reports/customer_support_evaluation.xlsx, reports/final_report.md and the experiment links in that report. Notebook replay uses saved artifacts; leave paid flags disabled.

Remaining checklist: record narration, review the recording, then submit through the course's requested channel. No recording or external submission has been made by this project.
