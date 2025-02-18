from daaily.lucy import Client
from daaily.lucy.constants import LUCY_V2_BASE_URL_STAGING

# Initialize the client
client = Client(base_url=LUCY_V2_BASE_URL_STAGING)

# Define the attribute
attribute = {
    "name_en": "New Attribute Test 1",
    "name_de": None,
    "type": "feature",
    "value_type": "string",
    "options": ["option1", "option2"],
    "status": "preview",
}

# Create the attribute
resp = client.attributes.create([attribute])

# Print the response
if resp.status == 200:
    print("Attribute created successfully")
    print(resp.json())
else:
    print("Failed to create attribute")
    print(resp.data)
