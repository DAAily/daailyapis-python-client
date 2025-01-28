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

updated_manufacturer = client.manufacturers.add_new_image_by_path(
    manufacturer_id, image_path, "logo"
)

print(updated_manufacturer.json())
