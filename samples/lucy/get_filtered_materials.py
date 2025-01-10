from daaily.lucy import Client, Filter

# Initialize the client
client = Client(base_url="https://lucy.staging.daaily.com/api/v2")

# Define filters
filters = [Filter("manufacturer_id", "3100860")]

# Search for materials matching the filters
materials = client.materials.get(filters=None)

# Iterate over the results
for m in materials:
    print(f"ID: {m['material_id']}, Name: {m['name_en']}, Status: {m['status']}")
