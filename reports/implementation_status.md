# Implementation status — November 2, 2026

All three 100-case runs are complete. Original baseline 91% accuracy; 2048-token control 96%; improved prompt 98%. Prompt comparison: 4 fixes, 2 regressions, 94 unchanged correct. The regressions (t058,t083) exhausted 2048 output tokens. Source labels and texts remain frozen; no failure was dropped or retried.

Known total including pilot: $0.79069535, excluding two original HTTP500 calls with unknown costs. Their full reservations remain in the append-only ledger, yielding $3.42083935 conservative exposure within the approved $5 ceiling.

Completed: reviewed dataset, model integration, LangSmith experiments/traces, three saved runs, paired comparisons, workbook, final report, notebook and demo outline. 42 offline tests pass; fresh-kernel notebook replay passes with all paid flags disabled. Workbook formulas/cached values match JSON metrics; original source-tab values and formulas are preserved. All paid processes have ended.

Remaining user action: record the narrated demo and submit the course artifacts. No external publication or submission was performed.

Limitations: synthetic correlated diagnosis set, one run per condition, model/provider variability, unknown original failure costs, and two remaining invalid responses. A previously reviewed minor remains: whitespace-only explanation text passes minimum-length validation; category correctness is independently scored.
