from daaily.lucy import Client
from daaily.lucy.constants import LUCY_V2_BASE_URL_STAGING
from daaily.similarity import Client as SimilarityClient

# Initialize the clients
client = Client(base_url=LUCY_V2_BASE_URL_STAGING)
similarity_client = SimilarityClient()

resp = client.products.get_by_id(20306944)

product = resp.json()

if not product or not product.get("images"):
    raise ValueError("Product has no images.")

similarities = similarity_client.compare_lucy_images(
    product["images"][0]["blob_id"],
    [
        "https://image.architonic.com/pro2-3/20306944/fino---03-smoke-20306944-1-pro-b-arcit18.png",
        "https://image.architonic.com/pfm3-3/2093192/fino-2019-fam-g-arcit18.jpg",
    ],
)

print(similarities)
