from daaily.lucy import Client, Filter

# Initialize the client
client = Client(base_url="https://lucy.staging.daaily.com/api/v2")

# Define filters
filters = [Filter("manufacturer_ids", "3100099,3100100,3100101")]

# Search for manufacturers matching the filters
manufacturers = client.manufacturers.get(filters=filters)

# Iterate over the results
for m in manufacturers:
    print(f"ID: {m['manufacturer_id']}, Name: {m['name']}, Status: {m['status']}")
