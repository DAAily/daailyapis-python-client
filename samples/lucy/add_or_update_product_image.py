import os

from daaily.lucy import Client
from daaily.lucy.constants import LUCY_V2_BASE_URL_STAGING

# Instantiate the client and overwrite the base URL with staging environment
client = Client(base_url=LUCY_V2_BASE_URL_STAGING)

# Get the directory of the current file
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define the product ID
product_id = 1032360

# Construct the path to the file in the neighboring directory
image_path = os.path.join(script_dir, "..", "assets", "vitra.jpeg")

# Test with image_url if image_path is None
image_path = None

# Define the image URL
image_url = "https://static.vitra.com/media-resized/dhL2lB0ZNN0glu8Gd_XqcH-2M7clCCI5bru3CZJ9yEI/fill/1440/810/ce/0/aHR0cHM6Ly9zdGF0aWMudml0cmEuY29tL21lZGlhL2Fzc2V0LzUzNTAyMDAvc3RvcmFnZS92X2Z1bGxibGVlZF8xNDQweC81ODkxMTcyNC5qcGc.jpg"

updated_product = client.products.add_or_update_product_image(
    product_id,
    image_path=image_path,
    image_url=image_url,
    description="Vitra chair",
    image_type="Ambient image",
    image_usages=["pro-g"],
    list_order=1,
    direct_link={
        "url": "https://static.vitra.com/media-resized/dhL2lB0ZNN0glu8Gd_XqcH-2M7clCCI5bru3CZJ9yEI/fill/1440/810/ce/0/aHR0cHM6Ly9zdGF0aWMudml0cmEuY29tL21lZGlhL2Fzc2V0LzUzNTAyMDAvc3RvcmFnZS92X2Z1bGxibGVlZF8xNDQweC81ODkxMTcyNC5qcGc.jpg",
        "is_enabled": True,
        "status": "ok",
        "last_crawled": "2025-02-12T09:00:00",
        "checked_at": "2025-02-13T12:34:00",
    },
)

print(updated_product.json())
