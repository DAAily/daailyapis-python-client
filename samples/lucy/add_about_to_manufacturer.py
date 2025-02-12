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

# Define about section details for a text-based about section
about_data = {
    "status": "online",
    "title_en": "About Our Company",
    "title_de": "Über unser Unternehmen",
    "title_it": "Chi siamo",
    "title_es": "Sobre nosotros",
    "title_fr": "À propos",
    "text_en": "Information in English",
    "text_de": "Information in German",
    "text_it": "Information in Italian",
    "text_es": "Information in Spanish",
    "text_fr": "Information in French",
    "list_order": 1,
}

result = client.manufacturers.add_about(
    manufacturer_id=manufacturer_id,
    about=about_data,
    content_type="picture",
    image_path=image_path,
)

print(f"{result.data}")
print(f"created: {result.json()}")
