import os

from daaily.lucy import Client
from daaily.lucy.constants import LUCY_V2_BASE_URL_STAGING

# Get the directory of the current file
script_dir = os.path.dirname(os.path.abspath(__file__))

# Instantiate the client and overwrite the base URL with staging environment
client = Client(base_url=LUCY_V2_BASE_URL_STAGING)

distributor_id = 8200464

try:
    signed_url = client.distributors.get_pdf_signed_url(
        distributor_id=distributor_id,
        pdf_title="design koln catalogue",
    )
    print("Pdf Signed Url:", signed_url)
except Exception as e:
    print(f"An error occurred while getting pdf signed url: {e}")


try:
    signed_url = client.distributors.get_pdf_preview_signed_url(
        distributor_id=distributor_id,
        mime_type="image/png",
    )
    print("Pdf Preview Signed Url:", signed_url)
except Exception as e:
    print(f"An error occurred while getting pdf preview signed url: {e}")
