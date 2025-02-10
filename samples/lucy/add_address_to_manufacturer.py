from daaily.lucy import Client
from daaily.lucy.constants import LUCY_V2_BASE_URL_STAGING

# Initialize the client
client = Client(base_url=LUCY_V2_BASE_URL_STAGING)

address = {
    "address_type": "country_representation",
    "homepage": "https://ambrite.ch",
    "city": "Zurich",
    "street": "Bahnhofstrasse 10",
    "zip": "8001",
    "contact_email": "volker@gmail.com",
    "contact_phone": "+41 44 123 45 67",
}
result = client.manufacturers.add_address(3100098, address, "CH")
print(f"{result.data}")
print(f"created: {result.json()}")
