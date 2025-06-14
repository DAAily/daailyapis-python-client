from daaily.lucy import Client, Filter
from daaily.lucy.constants import LUCY_V2_BASE_URL_STAGING

# Initialize the client
client = Client(base_url=LUCY_V2_BASE_URL_STAGING)

# Define filters
filters = [
    Filter("manufacturer_id", str(3103858)),
    Filter("status", "deleted"),
]

families = client.families.get(filters=filters)

# Iterate over the results
for f in families:
    print(f"ID: {f['family_id']}, Name: {f['name_en']}, Status: {f['status']}")
