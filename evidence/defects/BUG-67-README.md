# Bug 67 – Mark Order as Paid Dialogue Allows Empty Transaction Reference

## Defect Summary

During testing of the Saleor Order Management workflow, the **Mark Order as Paid** dialogue allowed an order to be marked as paid even when the **Transaction reference** field was left empty.

The payment was processed successfully, but the interface did not indicate that the transaction reference was optional. This may reduce payment traceability and cause confusion for administrators.

## Severity

**Medium**

## Preconditions

- A draft order has been finalized.
- The order is in the **Unfulfilled** state.

## Steps to Reproduce

1. Open the order in the Saleor Dashboard.
2. Click **Mark as Paid**.
3. Leave the **Transaction reference** field empty.
4. Confirm the payment.

## Expected Result

If the transaction reference is optional, the dialogue should clearly indicate this. Otherwise, the system should require a transaction reference before allowing the order to be marked as paid.

## Actual Result

The order was successfully marked as paid even though the transaction reference field was blank. No validation message or indication that the field was optional was displayed.

## Likely Cause

Source-code review of the Saleor order module indicated that the transaction reference is an optional input. The `external_reference` field can store an empty string, so no validation prevents the payment from being completed when the field is empty.

## Debugging Approach

The issue was reproduced several times through the Saleor Dashboard. The **Mark as Paid** workflow was traced through the `mark_order_as_paid_with_transaction()` function in:

`saleor/order/actions.py`

Manual code review and Ruff static analysis were used to examine the implementation. The investigation indicated that the behaviour is part of the current design rather than a runtime error.

## Current Status

The defect has been documented in **Azure DevOps as Bug #67**.

The issue does not prevent the payment workflow from functioning correctly. However, clearly identifying the transaction reference as optional, or requiring a value before marking the order as paid, would improve usability and payment traceability.

## Evidence

- Azure DevOps: **Bug #67**
- Report: **Section 16.3 – Defect Investigation 3**
- Figure 16.6 – Mark Order as Paid dialogue accepting an empty transaction reference
- Figure 16.7 – Source code showing the transaction reference is treated as an optional input
