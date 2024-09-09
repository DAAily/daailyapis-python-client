import asyncio

from dotenv import load_dotenv

from daaily.fifi.client import Client as FifiClient
from daaily.fifi.enums import FifiEndpoint, FifiProcessType

data = [
    {
        "image_path": "https://storage.googleapis.com/m-on-staging/12345678/product/13243546/new_space_test.jpeg"
    }
]


async def main():
    load_dotenv()
    client = FifiClient()
    response = await client.make_extract_request(
        FifiEndpoint.FIFI, FifiProcessType.IMAGES, data
    )
    print(response.data)


if __name__ == "__main__":
    asyncio.run(main())
