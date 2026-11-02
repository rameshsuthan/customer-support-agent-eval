# Routing policy v1

Chosen by Ramesh: route by the underlying problem, even if a refund is requested as a remedy.

| Route | Expected behavior |
|---|---|
| order_status | Tracking, delayed or missing delivery, including non-delivery with a refund request |
| product_issue | Damaged, incorrect, defective, incomplete, or misdescribed goods, including a refund remedy |
| refund_request | Return/cancellation for money back without an overriding delivery/product issue; refund follow-up |
| account_help | Login, account security, profile/address/payment-method updates, checkout session failure |
| other | General questions, feedback, stock/discount inquiries |

Review full tickets rather than isolated keywords. Unresolved cases must have a documented exclusion before dataset freezing. All 100 candidate labels are initially pending human review.

The baseline prompt adapts the simple category descriptions from The Gen Academy's starter notebook. It intentionally does not copy its improved prompt. The policy above defines ground truth for both of our runs; any prompt improvement will be chosen after our fresh baseline analysis.

## Human review amendment — November 2, 2026

Ramesh reviewed course-t004 through course-t007 and selected `refund_request` for all four. Explicit refund requests after non-delivery therefore override `order_status`. This specific decision supersedes the earlier general underlying-problem policy for this scenario. Damaged-product refund requests remain pending individual review.

Ramesh reviewed course-t044 through course-t047 and retained `product_issue`. Damaged-product refund requests stay with the product team; non-delivery refund requests route to the refund team. These are explicit business-policy distinctions, not a single universal intent-precedence rule.
