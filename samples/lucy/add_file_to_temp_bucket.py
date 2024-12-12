import os

from daaily.lucy import Client

# Get the directory of the current file
script_dir = os.path.dirname(os.path.abspath(__file__))

# Instantiate the client and overwrite the base URL with staging environment
client = Client(base_url="https://lucy.staging.daaily.com/api/v2")

product_id = 1032360

# Construct the path to the file in the neighboring directory
file_path = os.path.join(script_dir, "..", "assets", "vitra.jpeg")

try:
    blob_id = client.files.upload_file_to_temp_bucket_by_file_path(file_path)
    print("This is the blob_id of the uploaded asset:", blob_id)
except Exception as e:
    print(f"An error occurred: {e}")
