**Test Case 1**

Test Case ID: TC-CO-001

Title: Prevent Finalization of Draft Order Without Products

Purpose:
To verify that Saleor prevents a draft order from being finalized when it contains no products.

Preconditions:

* Administrator is logged into the Saleor Dashboard.
* Saleor 3.23 is running.
* A new draft order has been created in Channel-USD.
  
Test Data:

Field	Value
Products	None
Customer	Not selected
Shipping method	Not selected

Test Steps:

* Navigate to Fulfillment → Orders.
* Click Create Order.
* Select Channel-USD.
* Do not add any products.
* Click Finalize.
  
Expected Result:

The system should prevent finalization and display an error explaining that at least one product is required.


Actual Result:

The draft remained in the Draft state, and Saleor displayed:

"Could not create order without any products."

**Status: PASS**

<br><br>
**Test Case 2**

Test Case ID: TC-CO-002

Title: Prevent Fulfillment Before Payment Is Captured

Purpose:
To verify that an unfulfilled order cannot be fulfilled before payment has been captured.

Preconditions:

* A draft order has been finalized.
* The order status is Unfulfilled.
* No payment has been recorded.
* The order contains at least one product.
  
Test Data:

* Field	Value <br>
* Order number	21 <br>
* Product	Cubes Fountain Tee <br>
* Variant	M <br>
* Quantity	1 <br>
* Payment status	No payment received <br>
  
Test Steps:

* Open Order #21.
* Confirm that the payment summary shows No payment received.
* Locate the Fulfill button.
* Attempt to select or hover over the disabled Fulfill button.
  
Expected Result:
The Fulfill action should remain disabled, and the system should explain that payment must be captured first.

Actual Result:
The Fulfill button was disabled. The tooltip displayed:

"Can’t fulfill until payment is captured."

**Status: PASS**
<br>
<br>

**Test Case 3**

Test Case ID: TC-CO-003

Title: Fulfill a Paid Order Without a Tracking Number

Purpose:
To verify that a fully paid order can be fulfilled successfully when the optional tracking-number field is left empty.

Preconditions:

* The order status is Unfulfilled.
* Payment has been manually captured.
* The payment summary shows Fully charged.
* The product is available in the selected warehouse.
  
Test Data:

* Field	Value
* Order number	21
* Product	Cubes Fountain Tee
* Variant	M
* SKU	49182235821
* Fulfillment quantity	1
* Warehouse	Default Warehouse
* Tracking number	Blank
* Send fulfillment email	Selected

Test Steps:

* Open Order #21.
* Confirm that payment has been captured.
* Click Fulfill.
* Set the fulfillment quantity to 1.
* Select Default Warehouse.
* Leave the tracking-number field blank.
* Keep Send fulfillment email to customer selected.
* Click Fulfill.
* Open Mailpit and check the customer inbox.

Expected Result:

* The order should transition from Unfulfilled to Fulfilled.
* The product should move to the fulfilled order-lines section.
* Fulfillment should succeed without a tracking number.
* An order-fulfillment event should appear in Order History.
* A fulfillment email should be generated.

Actual Result:

* The order status changed to Fulfilled.
* The product moved to the fulfilled order-lines section.
* The Add tracking option became available.
* Order History recorded that the items were fulfilled.
* Mailpit received an email with the subject “Your order 21 has been fulfilled.”
  
**Status: PASS**

