import asyncio

from dotenv import load_dotenv

from daaily.sally.client import Client as SallyClient


async def main():
    load_dotenv()
    client = SallyClient()
    id_token = await client.get_token()
    print(id_token)


if __name__ == "__main__":
    asyncio.run(main())
