from daaily.lucy import Client
from daaily.lucy.constants import LUCY_V2_BASE_URL_STAGING

# Initialize the client
client = Client(base_url=LUCY_V2_BASE_URL_STAGING)

partial_product = client.products.deter_ownership_of_fields(
    20306944, ["name_en", "name_de", "live_link"], "justus.voigt@daaily.com"
)
if partial_product is not None:
    print(f"partial_product: {partial_product}")
