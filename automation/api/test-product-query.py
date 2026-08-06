import requests

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

response = requests.post(URL, json={"query": QUERY})

assert response.status_code == 200

data = response.json()

assert "data" in data
assert "products" in data["data"]
assert len(data["data"]["products"]["edges"]) > 0

print("PASS: GraphQL product query returned products successfully.")
