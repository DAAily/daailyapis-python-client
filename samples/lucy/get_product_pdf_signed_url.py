import os

from daaily.lucy import Client
from daaily.lucy.constants import LUCY_V2_BASE_URL_STAGING

# Get the directory of the current file
script_dir = os.path.dirname(os.path.abspath(__file__))

# Instantiate the client and overwrite the base URL with staging environment
client = Client(base_url=LUCY_V2_BASE_URL_STAGING)

product_id = 1032360

try:
    signed_url = client.products.get_pdf_signed_url(
        product_id=product_id,
        pdf_title="vitra product certification",
        pdf_type="certificate",
    )
    print("Pdf Signed Url:", signed_url)
except Exception as e:
    print(f"An error occurred while getting pdf signed url: {e}")


try:
    signed_url = client.products.get_pdf_preview_signed_url(
        product_id=product_id,
        mime_type="image/png",
        pdf_type="booklet",
    )
    print("Pdf Preview Signed Url:", signed_url)
except Exception as e:
    print(f"An error occurred while getting pdf preview signed url: {e}")
