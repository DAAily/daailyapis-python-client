from daaily.lucy import Client
from daaily.lucy.constants import LUCY_V2_BASE_URL_STAGING

# Initialize the client
client = Client(base_url=LUCY_V2_BASE_URL_STAGING)


is_up_to_date = client.products.deter_score_up_to_date(20306944)

print(f"Is up to date: {is_up_to_date}")
