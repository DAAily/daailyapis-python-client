import logging

from daaily.lucy import Client
from daaily.lucy.constants import LUCY_V2_BASE_URL_STAGING
from daaily.lucy.enums import Service

# from daaily.lucy.resources.attribute.types import AttributeType, AttributeValueUnit
from daaily.lucy.utils import setup_logging

# Setup logging
setup_logging(level=logging.INFO)

# Instantiate the client and overwrite the base URL with staging environment
client = Client(base_url=LUCY_V2_BASE_URL_STAGING)

attributes = [
    {
        "name": "dimension_height",
        "value": 3.3,
        "source_actor": "ai",
        "source_type": "html",
    },
    {
        "name": "dimension_width",
        "value": 2,
        "source_actor": "ai",
        "source_type": "html",
    },
    {
        "name": "dimension_length",
        "value": 38.4,
        "source_actor": "ai",
        "source_type": "html",
    },
    {
        "name": "feature_style",
        "value": "Modern",
        "source_actor": "ai",
        "source_type": "html",
    },
    {
        "name": "feature_lighting_installation_orientation",
        "value": True,
        "source_actor": "ai",
        "source_type": "html",
    },
]

# Define the product ID
product_id = 20321273

updated_product = client.products.add_or_update_attributes(
    product_id,
    attributes=attributes,
    service=Service.HOOVER,
    overwrite_existing=True,
    dry_run=False,
)

print(updated_product)
