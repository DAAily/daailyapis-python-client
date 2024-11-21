# Sample README for Using Daaily Lucy API Client

1. Basic usage of the Lucy client:
```bash
from daaily.lucy.client import Client as LucyClient
from daaily.lucy.enums import EntityType
from daaily.lucy.models import Filter


def main():
    lucy_client = LucyClient()
    
    # get a single collection
    response = lucy_client.get_collection(24574204)
    print("Collection: ", response.data)

    # get many manufacturers
    skip_filter = Filter(name="skip", value=str(0))
    limit_filter = Filter(name="limit", value=str(500))
    query_filters = [skip_filter, limit_filter]
    response = lucy_client.get_manufacturers(filters=query_filters)
    print("Manufacturers: ", response.data)

    # create many families
    family = {"name": "Test Family"}
    response = lucy_client.create_families([family])
    print("Created families: ", response.data)

    # update many materials
    material = {"id": 10037382, "name": "Test Material Updated"}
    response = lucy_client.update_materials([material])
    print("Updated materials: ", response.data)

    # get all products paginated
    response = lucy_client.get_paginated_entities(EntityType.PRODUCT)
    print("Products paginated: ", response)

    # get all products paginated with filters
    skip_filter = Filter(name="status", value="online")
    response = lucy_client.get_paginated_entities(
        EntityType.PRODUCT, filters=query_filters
    )
    print("Products paginated with filters: ", response)


if __name__ == "__main__":
    main()
```