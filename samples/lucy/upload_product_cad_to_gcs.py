import os

from daaily.lucy import Client
from daaily.lucy.constants import LUCY_V2_BASE_URL_STAGING

# Get the directory of the current file
script_dir = os.path.dirname(os.path.abspath(__file__))

# Instantiate the client and overwrite the base URL with staging environment
client = Client(base_url=LUCY_V2_BASE_URL_STAGING)

product_id = 1032360

# Construct the path to the file in the neighboring directory
cad_path = os.path.join(script_dir, "..", "assets", "vitra.dwg")

try:
    uploaded_cad = client.products.upload_cad(
        product_id=product_id,
        cad_path=cad_path,
        filename="vitra.dwg",
    )
    print("Uploaded cad to gcs with file path:", uploaded_cad)
except Exception as e:
    print(f"An error occurred while uploading cad to gcs: {e}")


try:
    with open(cad_path, "rb") as cad_file:
        cad_bytes = cad_file.read()
    uploaded_cad = client.products.upload_cad(
        product_id=product_id,
        cad_bytes=cad_bytes,
        filename="vitra.dwg",
        mime_type="image/vnd.dwg",
    )
    print("Uploaded cad to gcs with bytes:", uploaded_cad)
except Exception as e:
    print(f"An error occurred while uploading cad to gcs: {e}")
