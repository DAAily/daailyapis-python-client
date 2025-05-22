from daaily.lucy import Client
from daaily.lucy.constants import LUCY_V2_BASE_URL_STAGING

# Initialize the client
client = Client(base_url=LUCY_V2_BASE_URL_STAGING)

query = "height adjustable"

# Vector search for attributes
attributes = client.attributes.search(query=query, mode="vector", return_type="json")


# Iterate over the results
for a in attributes:
    print(f"ID: {a['attribute_id']}, Name: {a['name_en']}, Status: {a['status']}")
