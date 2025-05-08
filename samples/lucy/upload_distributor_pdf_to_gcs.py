import os

from daaily.lucy import Client
from daaily.lucy.constants import LUCY_V2_BASE_URL_STAGING

# Get the directory of the current file
script_dir = os.path.dirname(os.path.abspath(__file__))

# Instantiate the client and overwrite the base URL with staging environment
client = Client(base_url=LUCY_V2_BASE_URL_STAGING)

distributor_id = 8200464

# Construct the path to the file in the neighboring directory
pdf_path = os.path.join(script_dir, "..", "assets", "vitra.pdf")

try:
    uploaded_pdf = client.distributors.upload_pdf(
        distributor_id=distributor_id,
        pdf_path=pdf_path,
        filename="design-koln",
    )
    print("Uploaded pdf to gcs with file path:", uploaded_pdf)
except Exception as e:
    print(f"An error occurred while uploading pdf to gcs: {e}")


try:
    with open(pdf_path, "rb") as pdf_file:
        pdf_bytes = pdf_file.read()
    uploaded_pdf = client.distributors.upload_pdf(
        distributor_id=distributor_id,
        pdf_bytes=pdf_bytes,
        filename="design-koln",
        mime_type="application/pdf",
    )
    print("Uploaded pdf to gcs with bytes:", uploaded_pdf)
except Exception as e:
    print(f"An error occurred while uploading pdf to gcs: {e}")
