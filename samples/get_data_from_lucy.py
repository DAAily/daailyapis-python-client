import asyncio

from dotenv import load_dotenv

from daaily.lucy.client import Client as LucyClient
from daaily.lucy.enums import LucyEndpoint

params = {
    "manufacturer_id": 3100089,
}


async def main():
    load_dotenv()
    client = LucyClient()
    response = await client.get_entities(LucyEndpoint.FAMILY, params)
    print(response.data)


if __name__ == "__main__":
    asyncio.run(main())
