# Current routing policy — dataset v1

All 100 labels were explicitly human reviewed. The rules below supersede the initial policy draft preserved in the history afterward.

| Route | Reviewed boundary |
|---|---|
| `order_status` | Order location, unchanged/broken tracking, delayed delivery, and delivered-but-missing packages when no refund is explicitly requested |
| `refund_request` | Explicit refund requests after non-delivery; unopened returns, cancellations, overcharges, refund status, and preference for card refunds over store credit |
| `product_issue` | Damaged or wrong goods, missing instructions/damaged packaging, and reported description mismatch; damaged-product complaints remain here even with explicit refund requests |
| `account_help` | Login/session problems, unsolicited 2FA codes, stored address changes, and payment-method updates |
| `other` | Shipping-policy questions, positive feedback, stock inquiries, discount inquiries, and future-sale questions |

These are business-routing decisions: non-delivery refunds and damaged-product refunds have deliberately different ownership. Tags describe the request and are distinct from classifier-failure categories. Label review is complete; failure analysis follows our own measured baseline.

## Review history (earlier wording may be superseded above)

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

Ramesh approved course-t068 through course-t071 as `account_help`: logout/session failures during checkout route to account support, even when an order or product is mentioned.

Ramesh approved course-t056 through course-t059 as `product_issue`, with descriptive tags `damaged_packaging` and `missing_manual`. Tags add detail without changing the five routing categories and must not be confused with failure categories inferred from model errors.

Ramesh approved course-t052 through course-t055 as `product_issue`, tagged `description_mismatch`. This routes the customer-reported mismatch; it does not establish whether the advertising was objectively misleading.

Ramesh approved course-t024 through course-t027 as `refund_request`, tagged `refund_status`: questions about an already initiated refund concern money being returned rather than order delivery.

Ramesh approved course-t032 through course-t035 as `refund_request`, tagged `overcharge`: each customer explicitly requests a refund of the difference between the displayed and charged price.

Ramesh approved course-t036 through course-t039 as `refund_request`, tagged `refund_method_preference`: accepting store credit as an alternative does not remove the explicit preference for a refund to the original card.

Ramesh approved course-t016 through course-t019 as `order_status`, tagged `tracking_link_failure`: the technical problem blocks order tracking, with no stated login or account-access issue.

Ramesh approved course-t076 through course-t079 as `account_help`, tagged `account_security_concern`: unsolicited authentication codes indicate a reported security concern, not proof of compromise.

Ramesh approved course-t008 through course-t011 as `order_status`, tagged `delivered_not_received`: delivery is recorded but the customer cannot locate the package; no refund is explicitly requested.

Ramesh approved course-t012 through course-t015 as `order_status`, tagged `delivery_delay`: complaints about late delivery remain order-status tickets when no refund is explicitly requested.

Ramesh approved course-t000 through course-t003 as `order_status`, tagged `tracking_not_updated`: these seek order-location updates; unchanged tracking alone does not establish late delivery.

Ramesh approved course-t020 through course-t023 as `refund_request`, tagged `return_for_refund`: explicit return-for-money-back requests without a reported defect.

Ramesh approved the 10-ticket batch: course-t028–t031 as `refund_request` / `cancellation_refund`; course-t040–t043 as `product_issue` / `damaged_item`; course-t048–t049 as `product_issue` / `wrong_item_size`.

Ramesh approved course-t050–t051 as `product_issue` / `wrong_item_size`; course-t060–t063 as `account_help` / `login_failure`; course-t064–t067 as `account_help` / `payment_method_update`.

Ramesh approved course-t072–t075 as `account_help` / `address_update`; course-t080–t083 as `other` / `shipping_policy_inquiry`; course-t084–t085 as `other` / `positive_feedback`. Shipping-policy inquiries do not concern an existing order’s status.

Ramesh approved course-t086–t087 as `other` / `positive_feedback`; course-t088–t091 as `other` / `stock_availability`; course-t092–t095 as `other` / `discount_inquiry`. Order numbers or checkout references do not override a discount-inquiry intent.

Ramesh approved course-t096–t099 as `other` / `sale_inquiry`. All 100 case labels are now human reviewed.
