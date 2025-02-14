import os

from daaily.lucy import Client
from daaily.lucy.constants import LUCY_V2_BASE_URL_STAGING

# Instantiate the client and overwrite the base URL with staging environment
client = Client(base_url=LUCY_V2_BASE_URL_STAGING)

# Get the directory of the current file
script_dir = os.path.dirname(os.path.abspath(__file__))

family_id = 2014285

# Construct the path to the file in the neighboring directory
image_path = os.path.join(script_dir, "..", "assets", "vitra.jpeg")

# Test with image_url if image_path is None
updated_family = client.families.add_or_update_image(
    family_id,
    image_path=image_path,
    description="Vitra Chair Family",
    image_type="Ambient image",
    image_usages=["fam-g"],
    list_order=1,
    direct_link={
        "url": "https://www.vitra.com/en-us/family/alcove-plume-contract",
        "is_enabled": False,
        "status": "error",
        "last_crawled": "2021-09-29T09:00:00Z",
        "checked_at": "2023-10-29T09:00:00Z",
    },
)

print(updated_family.json())
