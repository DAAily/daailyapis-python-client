from daaily.lucy import Client
from daaily.lucy.constants import LUCY_V2_BASE_URL_STAGING

# Instantiate the client and overwrite the base URL with staging environment
client = Client(base_url=LUCY_V2_BASE_URL_STAGING)

# Define the product ID
manufacturer_id = 3100099

# Define blob_id to be move to different status
blob_id = (
    "m-on-staging/3100099/header/neue-werkstatt-by-lichtleuchten_header_c5a1e9c1"
    + ".jpeg/1739533979319187"
)

response = client.manufacturers.change_image_status(
    manufacturer_id, blob_id, "header", "deleted"
)

print(response.json())
