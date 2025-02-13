from daaily.lucy import Client, Filter
from daaily.lucy.constants import LUCY_V2_BASE_URL_STAGING

# Initialize the client
client = Client(base_url=LUCY_V2_BASE_URL_STAGING)

# Define filters
filters = [
    Filter("manufacturer_ids", "3100099,3100100,3100101"),
    Filter("status", "online,preview"),
]

# Search for manufacturers matching the filters
manufacturers = client.manufacturers.get(filters=filters)

# Iterate over the results
for m in manufacturers:
    print(f"ID: {m['manufacturer_id']}, Name: {m['name']}, Status: {m['status']}")
