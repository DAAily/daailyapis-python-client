from daaily.lucy import Client, Filter
from daaily.lucy.constants import LUCY_V2_BASE_URL_STAGING

# Initialize the client
client = Client(base_url=LUCY_V2_BASE_URL_STAGING)

# Define filters
filters = [
    Filter("status", "online"),
    Filter("skip", "580"),
]

products = client.products.get(filters=filters)

# Iterate over the results
for p in products:
    print(f"ID: {p['product_id']}, Name: {p['name_en']}, Status: {p['status']}")
