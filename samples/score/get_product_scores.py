from daaily.lucy import Client, Filter
from daaily.lucy.constants import LUCY_V2_BASE_URL_STAGING
from daaily.score import Product

# Initialize the client
client = Client(base_url=LUCY_V2_BASE_URL_STAGING)

# Initialize the score client
score = Product()

# Define filters
filters = [
    # Filter("manufacturer_id", "3100144"),
    Filter("product_ids", "1000528,1295461"),
    Filter("status", "online,preview,offline"),
]

# Search for products matching the filters
products = client.products.get(filters=filters)

# Iterate over the results
for i, p in enumerate(products):
    print(f"{i} Product: {p['product_id']}")
    score_results = score.score(p)
    print(f"Sum Score: {score_results.sum_score}")
    for sr in score_results.score_results:
        print(f"Field Name: {sr.field_name}")
        print(f"Field Score: {sr.score}")
        print(f"Weight: {sr.weight}")
        if sr.details:
            print(f"Richness: {sr.details.richness}")
            print(f"Completeness: {sr.details.completeness}")
            print(f"Length Factor: {sr.details.length_factor}")
            print(f"Flesch: {sr.details.flesch}")
            print(f"Grammar: {sr.details.grammar}")
            print(f"Spelling: {sr.details.spelling}")
        if sr.issues:
            print(f"Spelling: {sr.issues.spelling}")
            print(f"Grammar: {sr.issues.grammar}")
            print(f"Text: {sr.issues.text}")
        print(sr.to_dict())
    print("")
