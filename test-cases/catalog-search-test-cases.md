# Catalog and Search Test Cases

## TC-CS-01 – Retrieve Product List

**Purpose:** Verify that the Saleor GraphQL API can retrieve products from the product catalog.

**Preconditions:**
- Saleor 3.23 is running locally.
- User is logged into the Saleor Dashboard.
- GraphQL Playground is accessible.

**Test Data:** First 5 products.

**Steps:**
1. Open the GraphQL Playground.
2. Run a products query with `first: 5`.
3. Request the product ID, name, and slug.
4. Review the returned results.

**Expected Result:** The API returns up to five products with valid ID, name, and slug values.

**Actual Result:** The API successfully returned five products, including Apple Juice.

**Status:** PASS


## TC-CS-02 – Search Product by Keyword

**Purpose:** Verify that the product search returns a product matching the search keyword.

**Preconditions:**
- Saleor 3.23 is running locally.
- Product data is available in the catalog.
- GraphQL Playground is accessible.

**Test Data:** Search keyword: `Parrot`

**Steps:**
1. Open the GraphQL Playground.
2. Run a products query using the search filter `Parrot`.
3. Request the product ID, name, and slug.
4. Review the returned search results.

**Expected Result:** The API returns products matching the keyword `Parrot`.

**Actual Result:** The API returned `White Parrot Cushion API` with its ID and slug.

**Status:** PASS


## TC-CS-03 – Retrieve Product by ID

**Purpose:** Verify that a specific product can be retrieved using its GraphQL product ID.

**Preconditions:**
- Saleor 3.23 is running locally.
- GraphQL Playground is accessible.
- A valid product ID is available from the catalog.

**Test Data:** Product ID: `UHJvZHVjdDoxNjI=`

**Steps:**
1. Obtain the product ID from the product search result.
2. Run the `product` query using the selected ID.
3. Request the product ID, name, and slug.
4. Review the returned product.

**Expected Result:** The API returns the product associated with the supplied ID.

**Actual Result:** The API returned `White Parrot Cushion API` with ID `UHJvZHVjdDoxNjI=` and slug `white-parrot-cusion`.

**Status:** PASS
