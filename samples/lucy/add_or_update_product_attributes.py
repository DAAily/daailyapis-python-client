import logging

from daaily.lucy import Client
from daaily.lucy.constants import LUCY_V2_BASE_URL_STAGING
from daaily.lucy.enums import Service
from daaily.lucy.resources.attribute.types import AttributeType, AttributeValueUnit
from daaily.lucy.utils import setup_logging

# Setup logging
setup_logging(level=logging.INFO)

# Instantiate the client and overwrite the base URL with staging environment
client = Client(base_url=LUCY_V2_BASE_URL_STAGING)

attributes = [
    ("Cable length", 300, AttributeType.FEATURE, AttributeValueUnit.CM),
    ("Lighting installation orientation", "yes", AttributeType.FEATURE, None),
    (
        "3 star base",
        None,
        AttributeType.BASE,
        None,
    ),  # None value will be understood as being a boolean value for True
    ("Non existing attribute", None, AttributeType.FEATURE, None),
]

# Define the product ID
product_id = 20321273

updated_product = client.products.add_or_update_attributes(
    product_id,
    attributes=attributes,
    service=Service.HOOVER,
    overwrite_existing=False,
    dry_run=True,
)

print(updated_product)
