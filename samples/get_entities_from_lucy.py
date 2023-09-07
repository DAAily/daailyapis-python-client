from daaily.lucy.client import Client
from daaily.lucy.enums import EntityType


def main():
    client = Client()
    response = client.get_entities(EntityType.PRODUCT)
    print(response.data)


if __name__ == "__main__":
    main()
