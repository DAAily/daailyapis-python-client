import os

from daaily.lucy import Client

# Get the directory of the current file
script_dir = os.path.dirname(os.path.abspath(__file__))

# Instantiate the client and overwrite the base URL with staging environment
client = Client(base_url="https://lucy.staging.daaily.com/api/v2")

product_id = 1032360

# Construct the path to the file in the neighboring directory
image_path = os.path.join(script_dir, "..", "assets", "vitra.jpeg")

try:
    updated_product = client.products.add_image_by_path(product_id, image_path)
    print("Updated product information:", updated_product)
except Exception as e:
    print(f"An error occurred: {e}")
