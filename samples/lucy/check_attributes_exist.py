from daaily.lucy import Client
from daaily.lucy.constants import LUCY_V2_BASE_URL_STAGING
from daaily.lucy.resources.attribute.type import AttributeType

# Initialize the client
client = Client(base_url=LUCY_V2_BASE_URL_STAGING)

names_and_types = [
    ("Cable length", AttributeType.FEATURE),
    ("Lighting installation orientation", AttributeType.FEATURE),
    ("3 star base", AttributeType.BASE),
]
for name, attribute_type in names_and_types:
    existing_names = client.attributes.check_exists(
        name_en=name, attribute_type=attribute_type
    )
    print(existing_names)
    # Output:
    # {"Cable length": "feature_cable_length"}
    # {"Lighting installation orientation": "feature_lighting_installation_orientation"}
    # {"3 star base": "base_3_star"}
