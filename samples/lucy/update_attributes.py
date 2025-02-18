from daaily.lucy import Client, Filter
from daaily.lucy.constants import LUCY_V2_BASE_URL_STAGING

# Initialize the client
client = Client(base_url=LUCY_V2_BASE_URL_STAGING)

# Define filters
filters = [
    Filter("type", "category"),
    # Filter("status", "online"),
]

# Search for attributes matching the filters
attributes = client.attributes.get(filters=filters)

print(attributes)

# Iterate over the results
for a in attributes:
    if a["name_de"] is None:
        # add german name to the attribute
        a["name_de"] = "German Name"
        # update the attribute
        client.attributes.update([a])
