from daaily.lucy import Client, Filter
from daaily.score import Product

# Initialize the client
client = Client(base_url="https://lucy.staging.daaily.com/api/v2")

# Initialize the score client
score = Product()

# Define filters
filters = [
    Filter("manufacturer_id", "3100144"),
    Filter("status", "online,preview,offline"),
]

# Search for products matching the filters
products = client.products.get(filters=filters)

# Iterate over the results
for i, p in enumerate(products):
    print(f"{i} Product: {p['product_id']}")
    p["name_en"] = p.get("name_en", "").replace("\n", "")
    score_results = score.score(p)
    print(score_results)
    # print(f"{i} Product: {p['product_id']}-{p['name_en']} - score:{record_score}")
    print("")
