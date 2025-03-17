import logging

from daaily.lucy import Client
from daaily.lucy.constants import LUCY_V2_BASE_URL_STAGING
from daaily.lucy.enums import Service
from daaily.lucy.resources.attribute.type import AttributeType
from daaily.lucy.utils import setup_logging

# Setup logging
setup_logging(level=logging.INFO)

# Instantiate the client and overwrite the base URL with staging environment
client = Client(base_url=LUCY_V2_BASE_URL_STAGING)

attributes = [
    ("Cable length", "3 meters", AttributeType.FEATURE),
    ("Lighting installation orientation", "yes", AttributeType.FEATURE),
    (
        "3 star base",
        None,
        AttributeType.BASE,
    ),  # None value will be understood as being a boolean value for True
    ("Non existing attribute", None, AttributeType.FEATURE),
]

# Define the product ID
product_id = 20321273

updated_product = client.products.add_or_update_attributes(
    product_id, attributes=attributes, service=Service.HOOVER
)

print(updated_product.json())
