from daaily.lucy import Client
from daaily.lucy.constants import LUCY_V2_BASE_URL_STAGING

# Initialize the client
client = Client(base_url=LUCY_V2_BASE_URL_STAGING)

query = "lothar v"

# Vector search for creators
creators = client.creators.search(query=query, return_type="json")


# Iterate over the results
for c in creators:
    print(f"ID: {c['creator_id']}, Name: {c['name']}, Status: {c['status']}")
