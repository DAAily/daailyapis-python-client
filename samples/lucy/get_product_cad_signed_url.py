import os

from daaily.lucy import Client
from daaily.lucy.constants import LUCY_V2_BASE_URL_STAGING

# Get the directory of the current file
script_dir = os.path.dirname(os.path.abspath(__file__))

# Instantiate the client and overwrite the base URL with staging environment
client = Client(base_url=LUCY_V2_BASE_URL_STAGING)

product_id = 1032360

try:
    signed_url = client.products.get_cad_signed_url(
        product_id=product_id,
        file_extension="dwg",
        cad_title="vitra object",
    )
    print("Cad Signed Url:", signed_url)
except Exception as e:
    print(f"An error occurred while getting cad signed url: {e}")
