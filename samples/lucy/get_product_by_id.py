from daaily.lucy import Client

# Initialize the client
client = Client(base_url="https://lucy.staging.daaily.com/api/v2")

product = client.products.get_by_id(20306944)
print(f"product: {product.json()}")
