# Source reconciliation

Source revision: ef517b274cf86a2c4fa8ae72fdc89b3dce80f41d

- Workbook: 150 ticket rows, 29 failures, plus a separate EX teaching example.
- CSV: 100 ticket rows, 8 supplied baseline failures.
- Shared IDs: 100; only 1 have identical ticket text. IDs must not be used to join the two sources.
- Identical-text label disagreements: 2.

The workbook explicitly routes some refund requests by the requested remedy. The notebook CSV routes by underlying problem. Our initial policy matched the notebook's intent; subsequent human review changes the four non-delivery refund labels while retaining the damaged-product labels. These are different teaching datasets/results, not two runs of the same frozen dataset. Our own experiment uses the 100 CSV tickets after human review; supplied predictions are excluded from model inputs and are not our results.

## Identical-text disagreements

- CSV t004: I never received my order and I want my money back.
  - CSV: `order_status`; workbook: `refund_request`.
- CSV t044: My laptop arrived damaged and I want a full refund, not a replacement.
  - CSV: `product_issue`; workbook: `refund_request`.

## Attribution and license

Course files are unchanged local reference materials from The Gen Academy. The repository license endpoint returned 404; no redistribution license is assumed. Our Python implementation is written independently. Source redistribution/publication is outside the current scope.
