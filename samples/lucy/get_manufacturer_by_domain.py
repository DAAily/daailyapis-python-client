from daaily.lucy import Client
from daaily.lucy.constants import LUCY_V2_BASE_URL_STAGING

# Initialize the client
client = Client(base_url=LUCY_V2_BASE_URL_STAGING)

manufacturer = client.manufacturers.get_by_domain("minotti.com")
print(f"Manufacturer: {manufacturer.json()}")
