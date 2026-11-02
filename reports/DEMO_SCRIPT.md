# Demo script — approximately 4 minutes

Use this as a speaking guide, not a word-for-word reading requirement. Keep API keys, the `.env` file and unrelated account screens closed. Open the workbook, notebook and the two trace links from the solution PDF before recording.

## 0:00–0:35 — Introduce the project

**Show:** README or solution PDF, first page.

“For my Week 4 project, I evaluated a customer support routing agent. It classifies e-commerce tickets into five categories using Muse Spark Open through Fireworks AI. I used LangGraph for the classifier and LangSmith to inspect individual model calls. My goal was to measure reliability against a reviewed business policy, identify a failure pattern and test a focused improvement.”

## 0:35–1:15 — Explain the dataset and policy

**Show:** Our Reviewed Labels in the workbook. Point to t004 and t044.

“I reviewed all 100 supplied ticket labels before running the evaluation. An important business distinction is that a missing order with an explicit refund request goes to the refund team, while a damaged product stays with the product team even if the customer asks for money back. These are intentional routing decisions. I kept descriptive tags separate from the five categories and froze the labels so they would not change after I saw the model's answers.”

## 1:15–1:55 — Show the original failures

**Show:** Our Failure Analysis, then the original t044 result.

“The original run scored 91 percent. Its nine failures fell into four groups: four damaged-product/refund routing mistakes, one packaging-and-manual mistake, two incomplete responses at the output limit and two provider server errors. I kept every failed case in the score. I did not replace failures by retrying until they passed.”

## 1:55–2:35 — Explain the experiment design

**Show:** `prompts/improved.txt`, then Our Summary.

“Because some responses ran out of output space, I first increased the token limit from 1,024 to 2,048 without changing the prompt. This control scored 96 percent with all responses valid. Then I kept that limit fixed and added one routing-priority instruction: a damaged product stays in product_issue even when the customer requests a refund. Missing-order refund requests still go to refund_request. This separates the prompt comparison from the token-limit comparison.”

## 2:35–3:25 — Show a fix and a regression

**Show:** Improved t044 LangSmith trace, then t083. Expand ChatFireworks.

“The prompt edit fixed all four targeted damaged-laptop cases. Here, t044 now returns product_issue and its explanation refers to the priority rule. The overall score rose from 96 to 98 percent. But it was not a perfect improvement: t058 and t083 became invalid responses after using the full 2,048 output tokens. The traces confirm that they stopped because of length. So we gained four correct routes and lost two previously successful responses.”

## 3:25–4:15 — Conclude with cost, tradeoffs and limits

**Show:** Our Summary and the solution's limitations.

“The improved run's p95 latency was about 13.21 seconds, compared with 11.65 for the control. The known project cost, including the pilot, was about 79 cents, excluding two original requests whose usage was unknown. Conservative reserves kept the project within my five-dollar ceiling. The routing hypothesis worked on this set, but the 100-percent valid-response target was not met. My next investigation would focus on response completion using independent tickets. These cases are synthetic and related, and I reused the diagnosis set, so I am not claiming generalization or production readiness.”

## Likely follow-up questions

**Why not report 91% to 98% as the prompt gain?** The token limit also changed. The fair prompt comparison holds the limit at 2,048: 96% to 98%.

**Why do damaged-product refunds and missing-order refunds differ?** The human-reviewed policy assigns them to different support teams. The evaluation checks adherence to that policy, not a universal intent taxonomy.

**Why keep provider errors in accuracy?** A failed request does not route the ticket. Including it measures end-to-end performance; failure groups explain the cause separately.

**Did the higher limit solve truncation?** No. The control had no invalid outputs, but the improved prompt still had two. One run per condition cannot prove a general causal effect.

**Is this copied from the starter project?** The source tickets and simple baseline category descriptions are attributed. The reviewed labels, implementation, measured runs, failure analysis and prompt experiment were developed for this project with AI assistance.
