import os

from daaily.lucy import Client
from daaily.lucy.constants import LUCY_V2_BASE_URL_STAGING

# Get the directory of the current file
script_dir = os.path.dirname(os.path.abspath(__file__))

# Instantiate the client and overwrite the base URL with staging environment
client = Client(base_url=LUCY_V2_BASE_URL_STAGING)

product_id = 1032360

# Construct the path to the file in the neighboring directory
image_path = os.path.join(script_dir, "..", "assets", "vitra.jpeg")

try:
    uploaded_image = client.products.upload_image(
        product_id=product_id,
        image_path=image_path,
        filename="vitra.jpeg",
    )
    print("Uploaded image to gcs with file path:", uploaded_image)
except Exception as e:
    print(f"An error occurred while uploading image to gcs: {e}")


try:
    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()
    uploaded_image = client.products.upload_image(
        product_id=product_id,
        image_bytes=image_bytes,
        filename="vitra.jpeg",
        mime_type="image/jpeg",
    )
    print("Uploaded image to gcs with bytes:", uploaded_image)
except Exception as e:
    print(f"An error occurred while uploading image to gcs: {e}")
