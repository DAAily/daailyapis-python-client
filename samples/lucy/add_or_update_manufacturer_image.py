import os

from daaily.lucy import Client
from daaily.lucy.constants import LUCY_V2_BASE_URL_STAGING

# Instantiate the client and overwrite the base URL with staging environment
client = Client(base_url=LUCY_V2_BASE_URL_STAGING)

manufacturer_id = 3100099

# Get the directory of the current file
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the file in the neighboring directory
image_path = os.path.join(script_dir, "..", "assets", "vitra.jpeg")

image_path = None

image_url = "https://i0.wp.com/ideolux.it/wp-content/uploads/2021/03/Ideolux_Logo_White.png?fit=1584%2C254&ssl=1"

# Test with image_url if image_path is None
updated_manufacturer = client.manufacturers.add_or_update_image(
    manufacturer_id=manufacturer_id,
    image_type="logo",
    image_path=image_path,
    image_url=image_url,
    description="Header Image of Manufacturer",
    direct_link={
        "url": "https://www.vitra.com/en-us/family/alcove-plume-contract",
        "is_enabled": False,
        "status": "error",
        "last_crawled": "2021-09-29T09:00:00Z",
        "checked_at": "2023-10-29T09:00:00Z",
    },
)

print(updated_manufacturer.json())
