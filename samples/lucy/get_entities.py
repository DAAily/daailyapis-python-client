from daaily.lucy.client import Client
from daaily.lucy.constants import LUCY_V2_BASE_URL_STAGING
from daaily.lucy.enums import EntityType


def main():
    client = Client(base_url=LUCY_V2_BASE_URL_STAGING)
    response = client.get_entities(EntityType.PRODUCT)
    print(response.data)


if __name__ == "__main__":
    main()
