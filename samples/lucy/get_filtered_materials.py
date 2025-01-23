from daaily.lucy import Client, Filter
from daaily.lucy.constants import LUCY_V2_BASE_URL_STAGING

# Initialize the client
client = Client(base_url=LUCY_V2_BASE_URL_STAGING)

# Define filters
filters = [Filter("manufacturer_id", "3100860")]

# Search for materials matching the filters
materials = client.materials.get(filters=None)

# Iterate over the results
for m in materials:
    print(f"ID: {m['material_id']}, Name: {m['name_en']}, Status: {m['status']}")
