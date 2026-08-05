# Checkout & Order Lifecycle Exploration

---

## Investigation 1

### Can a draft order be finalized without products?

Result

No.

Business Rule

A draft order must contain at least one product before it can be finalized.

---

## Investigation 2

### What is the next validation after adding a product?

Observation

After adding a product, the product validation disappeared.

The system then reported:

- Shipping method required
- Shipping address missing
- Billing address missing

Business Rule

Products are validated before shipping information.

The workflow proceeds to address validation only after at least one order line exists.

---

## Investigation 3 - Can an Address Be Added Without Selecting a Customer?

### Observation

The customer, shipping address, and billing address fields were not directly editable.

The only available action was **Change customer**, which opened the customer selection process.

### Conclusion

For draft orders created through the Saleor Dashboard, staff must select an existing customer before customer address information can be used.

### Requirement Discovered

A draft order cannot proceed through the Dashboard address workflow until a customer has been selected.

---

## Investigation 4 - Customer and Address Selection

### Objective

Determine what happens after selecting a customer.

### Observation

After selecting an existing customer, Saleor immediately opened a dialog asking for a shipping address.

The dialog provides two options:

- Use one of the customer's saved addresses.
- Add a new address manually.

### Business Rules Discovered

- Customer selection occurs before address selection.
- A customer may have multiple saved addresses.
- Staff can create a new shipping address while creating the draft order.

---

## Investigation 5 - Customer Address Assignment

### Objective

Determine what happens after selecting an existing customer and one of their saved addresses.

### Steps

1. Selected customer: melissa.sanders@example.com
2. Chose an existing saved address.

### Observations

- Customer information was populated.
- Shipping address was populated.
- Billing address was populated.
- "View orders" and "View profile" links became available.
- Both addresses remained editable.
- The previous address validation errors disappeared.

### Remaining Validation

The system now reports:

> Shipping method is required for this order.

### Business Rule Discovered

Once valid customer and address information is supplied, Saleor advances to shipping method validation before allowing the draft order to be finalized.

---

## Investigation 6 - Finalizing the Draft Order

### Objective

Determine what happens after all required draft order information is provided.

### Steps

1. Added a product.
2. Selected a customer.
3. Selected shipping and billing addresses.
4. Selected the "Default" shipping method.
5. Clicked **Finalize**.

### Result

The draft order was successfully converted into an order.

### State Transition

Draft → Unfulfilled

### New Features Available

- Fulfill
- Mark as Paid
- Return
- Generate Invoice

### Observation

These actions become available only after the order has been finalized.

---

## Investigation 7 - Manual Payment Confirmation

### Objective

Determine how payment is recorded for a manually created order.

### Observation

Clicking **Mark as Paid** opens a dialog requesting a transaction reference.

### Business Rule

Payment is not automatically captured. An administrator must manually confirm payment by providing a transaction reference.

### Evidence

The dialog requires a transaction reference before the order can be marked as paid.

---

## Investigation 8 - Transaction Reference Validation

### Objective

Determine whether a transaction reference is mandatory when manually marking an order as paid.

### Steps

1. Clicked **Mark as Paid**.
2. Left the transaction reference field blank.
3. Clicked **Mark as Paid**.

### Result

The order was successfully marked as paid.

### Observation

No validation error was displayed.

The payment summary changed to:

- Fully charged
- Fully authorised

The Fulfill button became enabled.

### Possible Improvement

The dialog requests a transaction reference but does not require one. This should be verified against the intended business requirements.

---

## Investigation 9 - Fulfillment Quantity Boundaries

### Objective

Determine the allowed quantity range when fulfilling an order line.

### Test Data

- Product: Cubes Fountain Tee
- Variant: M
- Ordered quantity: 1
- Available stock: 412

### Observation

The fulfillment quantity field was editable.

- The quantity could be reduced from 1 to 0.
- The quantity could not be reduced below 0.
- The quantity could not be increased above 1.

### Conclusion

Saleor limits the fulfillment quantity to the remaining unfulfilled quantity for the order line.

### Business Rules Discovered

- Fulfillment quantity cannot be negative.
- Fulfillment quantity cannot exceed the quantity ordered.
- A value of 0 excludes the line from the current fulfillment.

---

## Investigation 10 - Order Fulfillment

### Objective

Determine what happens after fulfilling a paid order.

### Steps

1. Opened a paid order.
2. Clicked Fulfill.
3. Accepted the default warehouse.
4. Left tracking number blank.
5. Completed fulfillment.

### Result

The order status changed from:

Unfulfilled

to

Fulfilled

### Observations

- Product moved into the Fulfilled section.
- Payment remained Fully Charged.
- Add Tracking became available.
- Transaction remained successful.
- Order History recorded the fulfillment event.

### Business Rules

- Orders must be paid before fulfillment.
- Tracking number is optional during fulfillment.
- Tracking information can be added after fulfillment.

---

## Investigation 11 - Return Workflow

### Objective

Determine the options available after a fulfilled order is returned.

### Observations

The Return & Replace screen allows:

- Return quantity
- Replace item
- Refund
- Refund shipment
- Refund value
- Return reason
- Return notes

### Business Rules

- Returned quantity cannot exceed fulfilled quantity.
- Replacement creates a new draft order.
- Returning and refunding are separate operations.
- Refund is optional.

---


## Workflow Discoveries

1. Draft orders may exist without products.

2. Draft orders cannot be finalized without products.

3. Once products are added, Saleor validates shipping information.

4. Draft orders remain editable.
