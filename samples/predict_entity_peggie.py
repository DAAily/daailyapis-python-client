import asyncio

from dotenv import load_dotenv

from daaily.peggie.client import Client as PeggieClient
from daaily.peggie.enums import PeggieEndpoint

data = [
    {
        "file_type": "image/jpeg",
        "list_order": "001",
        "collection_name_en": [],
        "family_name_en": "Inverso",
        "product_name_en": "Ventaglio",
        "file_name": "PF72007.jpg",
        "image_type": "Cut-out image",
        "image_usages": ["pro-sq", "pro-b"],
        "sku": "72007",
    },
    {
        "file_type": "image/jpeg",
        "list_order": "013",
        "collection_name_en": [],
        "family_name_en": "Inverso",
        "product_name_en": "Ventaglio",
        "file_name": "PF72028.jpg",
        "image_type": "Drawing image",
        "image_usages": ["pro-g"],
        "sku": "72028",
    },
]


async def main():
    load_dotenv()
    client = PeggieClient()
    response = await client.make_predict_request(
        PeggieEndpoint.PREDICT_IMAGE_USAGE_TEMP_ID, data
    )
    print(response.data)


if __name__ == "__main__":
    asyncio.run(main())
