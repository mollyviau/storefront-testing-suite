"""
Automated Test 2 - Product catalog retrieval through the GraphQL API.

Owner: Van Trinh Nguyen
Workflow: Product Catalog and Search
Traces to: TC-PC-01

This test exercises service-level behaviour by querying the GraphQL endpoint
directly, and satisfies the "test of logic, service, or code-level behaviour"
half of the required automation mix.

Requires a running Saleor instance. Marked `live` so that it is excluded from
the continuous integration run, which cannot stand up the full stack.

Run locally with:
    pytest api
"""

import pytest
import requests

pytestmark = pytest.mark.live

URL = "http://localhost:8000/graphql/"

QUERY = """
query {
  products(first: 5, channel: "default-channel") {
    edges {
      node {
        id
        name
        slug
      }
    }
  }
}
"""


def test_product_query():
    """
    TC-PC-01 - the products connection returns a page of product records with
    valid id, name and slug values for a valid channel.
    """
    response = requests.post(URL, json={"query": QUERY}, timeout=30)

    assert response.status_code == 200

    data = response.json()

    assert "data" in data
    assert "products" in data["data"]

    edges = data["data"]["products"]["edges"]
    assert len(edges) > 0

    # Every returned product carries the three requested fields.
    for edge in edges:
        node = edge["node"]
        assert node["id"]
        assert node["name"]
        assert node["slug"]
