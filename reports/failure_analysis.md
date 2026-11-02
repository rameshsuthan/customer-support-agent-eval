# Baseline failure analysis — pending human review

All 100 frozen v1 tickets were attempted once. The original experiment and two continuations are combined by case ID locally; no failed case was retried. LangSmith continuation views alone do not represent the full 100-case baseline.

Accuracy 91%; macro F1 0.926638; valid response rate 96%; p95 latency16.8619 seconds. Targets: accuracy ≥95% not met; macro F1 ≥0.90 met; valid 100% not met; p95 ≤15 seconds not met. Mean cost target cannot be assessed with two unknown-cost requests. Known baseline estimate $0.23935465 with 98% cost coverage; pilot adds $0.0132835. Conservative project budget exposure $2.88278215 includes two $1.315072 unknown-cost reserves and is not an invoice. Approved project ceiling $5.

| Failure group | Cases | Count | Interpretation |
|---|---|---:|---|
| Damaged product + refund priority | t044–t047 | 4 | Baseline omits the reviewed tie-break rule; model prioritizes money back. |
| Packaging/manual scope | t059 | 1 | Baseline definition omits packaging and missing documentation; model treats it as feedback. |
| Output budget exhaustion | t015,t058 | 2 | 1024 output tokens, including 1021 reasoning tokens; no valid classification. |
| Provider HTTP 500 | t026,t055 | 2 | Infrastructure failure; usage unknown. |

The five routing errors are policy-adherence failures against our frozen reviewed labels, not evidence that the customer's preferred outcome is unreasonable. Product issues routed to refund/general queues could require transfers and delay handling; no monetary loss is estimated. Invalid/server responses leave a ticket unrouted and require operational handling.

## Proposed single prompt change

Add an explicit priority rule for damaged/defective/wrong/not-as-described products versus refund wording. Preserve missing-delivery+refund routing as refund_request. Leave the packaging/manual definition and output cap unchanged in this experiment to keep the intervention focused.

Hypothesis: correct the four damaged-laptop/refund cases without regressing the four missing-delivery/refund cases (t004–t007). A plausible regression is over-routing ordinary refund requests to product_issue. Reevaluate all 100 cases; record all regressions. Remaining packaging/manual and infrastructure failures may persist. Any improvement in HTTP 500 cases must not be attributed to the prompt.

Ramesh approved the routing-failure interpretations and the focused prompt experiment. He additionally approved raising the output limit to2048, with a separate unchanged-prompt control at2048 before the improved prompt run. The original1024-token baseline is preserved. Packaging/manual wording remains unchanged.

## Individual failures

### course-t015 — output_budget_exhaustion

Ticket: I thought I paid for 2-day shipping. It’s been 9 days already—what’s taking so long?

Reviewed label: `order_status`; prediction: `invalid`. Output reached 1024 tokens, 1021 reasoning tokens; no valid structured prediction. LangSmith trace confirms finish_reason=length.

[Trace](https://smith.langchain.com/o/82c36783-971e-46c1-862e-a27d43bbcba3/projects/p/15f3f758-548f-4fd1-b994-c71bdd40d11b/trace/01a19dd1-52be-725f-81e1-3a9eb8c8d895/run/01a19dd1-52be-725f-81e1-3a9eb8c8d895?start_time=2026-11-02T19%3A51%3A43.550728%2B00%3A00)

### course-t026 — provider_http_500

Ticket: Hi there, I hope you’re doing well. I wanted to inquire about my refund for the item I returned (order #9876) two weeks ago; unfortunately, it hasn’t appeared on my card yet. Could you please help me with this?

Reviewed label: `refund_request`; prediction: `error`. Provider trace confirms HTTP 500; no classification or usage. Actual cost remains unknown.

[Trace](https://smith.langchain.com/o/82c36783-971e-46c1-862e-a27d43bbcba3/projects/p/efa627bd-6463-4b5e-9044-6d1319cecbaa/trace/01a19dc1-3256-7f6e-bb46-b9fd14ee267a/run/01a19dc1-3256-7f6e-bb46-b9fd14ee267a?start_time=2026-11-02T19%3A34%3A06.678349%2B00%3A00)

### course-t044 — damaged_product_refund_priority

Ticket: My laptop arrived damaged and I want a full refund, not a replacement.

Reviewed label: `product_issue`; prediction: `refund_request`. Model prioritizes explicit refund wording. Reviewed policy prioritizes damaged product. Baseline prompt omits the tie-break rule.

[Trace](https://smith.langchain.com/o/82c36783-971e-46c1-862e-a27d43bbcba3/projects/p/f512963c-b927-4465-911c-4f2324bac698/trace/01a19de0-353f-7c16-9743-97065b819c2e/run/01a19de0-353f-7c16-9743-97065b819c2e?start_time=2026-11-02T20%3A07%3A59.039187%2B00%3A00)

### course-t045 — damaged_product_refund_priority

Ticket: I received my laptop in awful condition and I'm not interested in a replacement. I just want my money back, please.

Reviewed label: `product_issue`; prediction: `refund_request`. Model prioritizes explicit refund wording. Reviewed policy prioritizes damaged product. Baseline prompt omits the tie-break rule.

[Trace](https://smith.langchain.com/o/82c36783-971e-46c1-862e-a27d43bbcba3/projects/p/f512963c-b927-4465-911c-4f2324bac698/trace/01a19dd9-fa59-7577-8108-2d6ac389a173/run/01a19dd9-fa59-7577-8108-2d6ac389a173?start_time=2026-11-02T20%3A01%3A10.745977%2B00%3A00)

### course-t046 — damaged_product_refund_priority

Ticket: Hey, my laptop showed up damaged, and I would prefer to get a full refund instead of receiving a new one.

Reviewed label: `product_issue`; prediction: `refund_request`. Model prioritizes explicit refund wording. Reviewed policy prioritizes damaged product. Baseline prompt omits the tie-break rule.

[Trace](https://smith.langchain.com/o/82c36783-971e-46c1-862e-a27d43bbcba3/projects/p/f512963c-b927-4465-911c-4f2324bac698/trace/01a19dda-3a46-7041-8d09-9a8fc9869fd6/run/01a19dda-3a46-7041-8d09-9a8fc9869fd6?start_time=2026-11-02T20%3A01%3A27.110787%2B00%3A00)

### course-t047 — damaged_product_refund_priority

Ticket: The laptop I ordered is broken, and I refuse to accept a replacement. I simply want a complete refund.

Reviewed label: `product_issue`; prediction: `refund_request`. Model prioritizes explicit refund wording. Reviewed policy prioritizes damaged product. Baseline prompt omits the tie-break rule.

[Trace](https://smith.langchain.com/o/82c36783-971e-46c1-862e-a27d43bbcba3/projects/p/f512963c-b927-4465-911c-4f2324bac698/trace/01a19dd7-9d37-7070-84bf-8180479560f2/run/01a19dd7-9d37-7070-84bf-8180479560f2?start_time=2026-11-02T19%3A58%3A35.831722%2B00%3A00)

### course-t055 — provider_http_500

Ticket: It's frustrating to see that the item I ordered, which was labeled as 'wireless', actually requires a separate dongle to function. That's definitely not what I expected.

Reviewed label: `product_issue`; prediction: `error`. Provider trace confirms HTTP 500; no classification or usage. Actual cost remains unknown.

[Trace](https://smith.langchain.com/o/82c36783-971e-46c1-862e-a27d43bbcba3/projects/p/15f3f758-548f-4fd1-b994-c71bdd40d11b/trace/01a19dd4-b168-71bd-a78b-06a752704fe0/run/01a19dd4-b168-71bd-a78b-06a752704fe0?start_time=2026-11-02T19%3A55%3A24.392423%2B00%3A00)

### course-t058 — output_budget_exhaustion

Ticket: I received my order, and while the product itself is okay, the box is all smashed up, and I can't find the instructions anywhere.

Reviewed label: `product_issue`; prediction: `invalid`. Output reached 1024 tokens, 1021 reasoning tokens; no valid structured prediction. LangSmith trace confirms finish_reason=length.

[Trace](https://smith.langchain.com/o/82c36783-971e-46c1-862e-a27d43bbcba3/projects/p/f512963c-b927-4465-911c-4f2324bac698/trace/01a19de1-31d4-70d1-8084-011689f4e193/run/01a19de1-31d4-70d1-8084-011689f4e193?start_time=2026-11-02T20%3A09%3A03.700056%2B00%3A00)

### course-t059 — packaging_manual_scope

Ticket: The item works great, but I'm really disappointed that the box is completely wrecked and I didn’t get the manual.

Reviewed label: `product_issue`; prediction: `other`. Model treats damaged packaging and missing manual as general feedback because the item works. Reviewed product_issue includes these concerns; baseline definition omits them.

[Trace](https://smith.langchain.com/o/82c36783-971e-46c1-862e-a27d43bbcba3/projects/p/f512963c-b927-4465-911c-4f2324bac698/trace/01a19dde-961e-72c3-92e0-55d4d17b2a7a/run/01a19dde-961e-72c3-92e0-55d4d17b2a7a?start_time=2026-11-02T20%3A06%3A12.766474%2B00%3A00)

## Sample of passes

Inspected model-child traces for t000 (tracking), t004 (non-delivery refund), t040 (damaged item), t056 (packaging/manual), t060 (login), and t080 (shipping policy). All matched reviewed labels and finished normally. This sample supports those individual outcomes, not a claim that all explanations were reviewed. Evidence: reports/trace_evidence/baseline_samples.json. The packaging/manual family is inconsistent: t056/t057 pass, t058 hits the output limit, and t059 routes to other.

## Limits

The 100 synthetic tickets form 25 seed families. Diagnosis and reevaluation use the same set, so gains measure exercise-set improvement rather than held-out generalization. One observed run per prompt cannot separate prompt effects fully from generation variability or provider conditions. No labels changed after viewing predictions.
