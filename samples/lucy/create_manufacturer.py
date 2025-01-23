from daaily.lucy import Client
from daaily.lucy.constants import LUCY_V2_BASE_URL_STAGING

# Initialize the client
client = Client(base_url=LUCY_V2_BASE_URL_STAGING)

manufacturer = {
    "name": "ambrite AG",
    "status": "preview",
    "domain": "ambrite.ch",
    "platforms": ["new_architonic"],
    "addresses": [
        {
            "address_type": "headquarter",
            "country_id": "8992187",
            "homepage": "https://ambrite.ch",
        }
    ],
}
result = client.manufacturers.create(manufacturers=[manufacturer])
print(f"{result.data}")
print(f"created: {result.json()}")
