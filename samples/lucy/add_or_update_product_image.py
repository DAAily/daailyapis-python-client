import os

from daaily.lucy import Client
from daaily.lucy.constants import LUCY_V2_BASE_URL_STAGING

# Instantiate the client and overwrite the base URL with staging environment
client = Client(base_url=LUCY_V2_BASE_URL_STAGING)

# Get the directory of the current file
script_dir = os.path.dirname(os.path.abspath(__file__))

product_id = 1032360

# Construct the path to the file in the neighboring directory
image_path = os.path.join(script_dir, "..", "assets", "vitra.jpeg")

updated_product = client.products.add_or_update_product_image(
    product_id,
    image_path,
    description="Vitra chair",
    image_type="Ambient image",
    image_usages=["pro-g"],
    list_order=1,
    direct_link={
        "url": "https://www.vitra.com/en-us/product/alcove-plume-contract",
        "is_enabled": False,
        "status": "error",
        "last_crawled": "2021-09-29T09:00:00Z",
        "checked_at": "2023-10-29T09:00:00Z",
    },
)

print(updated_product.json())
