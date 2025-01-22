import asyncio

from daaily.lucy import Client
from daaily.lucy.constants import LUCY_V2_BASE_URL_STAGING


# An async helper to fetch a single product
async def fetch_product(client: Client, product_id):
    """
    Wrap the synchronous client.products.get_by_id call
    so it can be awaited in an async context.
    """
    product = await asyncio.to_thread(client.products.get_by_id, product_id)
    return product


async def main():
    product_ids = [20290832, 20290822, 20290820]

    # Initialize the client
    client = Client(base_url=LUCY_V2_BASE_URL_STAGING)

    # Create a list of tasks for concurrent/parallel fetching
    tasks = [asyncio.create_task(fetch_product(client, pid)) for pid in product_ids]

    # Fire off all requests in parallel using asyncio.gather
    products = await asyncio.gather(*tasks)

    # Print the results
    for product in products:
        print(f"product: {product.json()}")


if __name__ == "__main__":
    asyncio.run(main())
