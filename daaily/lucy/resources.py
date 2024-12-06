from typing import TYPE_CHECKING, Any, Dict, Generator

from daaily.lucy.enums import EntityType
from daaily.lucy.models import Filter

if TYPE_CHECKING:
    from daaily.lucy.client import Client


class BaseResource:
    def __init__(self, client: "Client"):
        self._client: "Client" = client

    def get(self, filters: list[Filter] | None = None):
        raise NotImplementedError

    def get_by_id(self, entity_id: int):
        raise NotImplementedError

    def update(self, data: list[dict], filters: list[Filter] | None = None):
        raise NotImplementedError

    def create(self, data: list[dict], filters: list[Filter] | None = None):
        raise NotImplementedError


class ManufacturersResource(BaseResource):
    def get(
        self, filters: list[Filter] | None = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Retrieves manufacturers with optional filtering, returning them as a generator
        that yields each manufacturer one at a time.

        Available filters:
            - manufacturer_ids (str): Filter by comma seperated manufacturer IDs.
            - manufacturer_name (str): Filter by manufacturer name.

        Note that the following filters are automatically added to the query:
            - skip (int): Number of records to skip.
            - limit (int): Maximum number of records to retrieve.

        Args:
            filters (list[Filter] | None): A list of filters to apply to the query.

        Yields:
            dict: A dictionary representing a single manufacturer.

        Example:
            ```python
            # Define filters
            filters = [Filter("manufacturer_ids", "3100099,3100100,3100101")]

            # Get manufacturers (pagination handled internally)
            manufacturers = client.manufacturers.get(filters=filters)

            # Iterate over the results without worrying about pagination
            for m in manufacturers:
                print(f"ID: {m['manufacturer_id']}, Name: {m['name']}")
            ```
        """
        if filters is None:
            filters = []
        filters = [f for f in filters if f.name not in ["limit", "skip"]]
        limit_filter = Filter(name="limit", value="100")
        skip_filter = Filter(name="skip", value="0")
        filters.append(limit_filter)
        filters.append(skip_filter)
        while True:
            response = self._client.get_entities(EntityType.MANUFACTURER, filters)
            if response.status == 404:
                break
            for item in response.json():
                yield item
            skip = int(skip_filter.value) + int(limit_filter.value)
            skip_filter.value = str(skip)
            filters = [f for f in filters if f.name != "skip"]
            filters.append(skip_filter)

    def get_by_id(self, manufacturer_id: int):
        return self._client.get_entity(EntityType.MANUFACTURER, manufacturer_id)

    def update(self, manufacturers: list[dict], filters: list[Filter] | None = None):
        return self._client.update_entities(
            EntityType.MANUFACTURER, manufacturers, filters
        )

    def create(self, manufacturers: list[dict], filters: list[Filter] | None = None):
        return self._client.create_entities(
            EntityType.MANUFACTURER, manufacturers, filters
        )


class DistributorsResource(BaseResource):
    def get(self, filters: list[Filter] | None = None):
        return self._client.get_entities(EntityType.DISTRIBUTOR, filters)

    def get_by_id(self, distributor_id: int):
        return self._client.get_entity(EntityType.DISTRIBUTOR, distributor_id)

    def update(self, distributors: list[dict], filters: list[Filter] | None = None):
        return self._client.update_entities(
            EntityType.DISTRIBUTOR, distributors, filters
        )

    def create(self, distributors: list[dict], filters: list[Filter] | None = None):
        return self._client.create_entities(
            EntityType.DISTRIBUTOR, distributors, filters
        )


class CollectionsResource(BaseResource):
    def get(self, filters: list[Filter] | None = None):
        return self._client.get_entities(EntityType.COLLECTION, filters)

    def get_by_id(self, collection_id: int):
        return self._client.get_entity(EntityType.COLLECTION, collection_id)

    def update(self, collections: list[dict], filters: list[Filter] | None = None):
        return self._client.update_entities(EntityType.COLLECTION, collections, filters)

    def create(self, collections: list[dict], filters: list[Filter] | None = None):
        return self._client.create_entities(EntityType.COLLECTION, collections, filters)


class JournalistsResource(BaseResource):
    def get(self, filters: list[Filter] | None = None):
        return self._client.get_entities(EntityType.JOURNALIST, filters)

    def get_by_id(self, journalist_id: int):
        return self._client.get_entity(EntityType.JOURNALIST, journalist_id)

    def update(self, journalists: list[dict], filters: list[Filter] | None = None):
        return self._client.update_entities(EntityType.JOURNALIST, journalists, filters)

    def create(self, journalists: list[dict], filters: list[Filter] | None = None):
        return self._client.create_entities(EntityType.JOURNALIST, journalists, filters)


class MaterialsResource(BaseResource):
    def get(self, filters: list[Filter] | None = None):
        return self._client.get_entities(EntityType.MATERIAL, filters)

    def get_by_id(self, material_id: int):
        return self._client.get_entity(EntityType.MATERIAL, material_id)

    def update(self, materials: list[dict], filters: list[Filter] | None = None):
        return self._client.update_entities(EntityType.MATERIAL, materials, filters)

    def create(self, materials: list[dict], filters: list[Filter] | None = None):
        return self._client.create_entities(EntityType.MATERIAL, materials, filters)


class ProjectsResource(BaseResource):
    def get(self, filters: list[Filter] | None = None):
        return self._client.get_entities(EntityType.PROJECT, filters)

    def get_by_id(self, project_id: int):
        return self._client.get_entity(EntityType.PROJECT, project_id)

    def update(self, projects: list[dict], filters: list[Filter] | None = None):
        return self._client.update_entities(EntityType.PROJECT, projects, filters)

    def create(self, projects: list[dict], filters: list[Filter] | None = None):
        return self._client.create_entities(EntityType.PROJECT, projects, filters)


class ProductsResource(BaseResource):
    def get(self, filters: list[Filter] | None = None):
        return self._client.get_entities(EntityType.PRODUCT, filters)

    def get_by_id(self, product_id: int):
        return self._client.get_entity(EntityType.PRODUCT, product_id)

    def update(self, products: list[dict], filters: list[Filter] | None = None):
        return self._client.update_entities(EntityType.PRODUCT, products, filters)

    def create(self, products: list[dict], filters: list[Filter] | None = None):
        return self._client.create_entities(EntityType.PRODUCT, products, filters)


class CreatorsResource(BaseResource):
    def get(self, filters: list[Filter] | None = None):
        return self._client.get_entities(EntityType.CREATOR, filters)

    def get_by_id(self, creator_id: int):
        return self._client.get_entity(EntityType.CREATOR, creator_id)

    def update(self, creators: list[dict], filters: list[Filter] | None = None):
        return self._client.update_entities(EntityType.CREATOR, creators, filters)

    def create(self, creators: list[dict], filters: list[Filter] | None = None):
        return self._client.create_entities(EntityType.CREATOR, creators, filters)


class FamiliesResource(BaseResource):
    def get(self, filters: list[Filter] | None = None):
        return self._client.get_entities(EntityType.FAMILY, filters)

    def get_by_id(self, family_id: int):
        return self._client.get_entity(EntityType.FAMILY, family_id)

    def update(self, families: list[dict], filters: list[Filter] | None = None):
        return self._client.update_entities(EntityType.FAMILY, families, filters)

    def create(self, families: list[dict], filters: list[Filter] | None = None):
        return self._client.create_entities(EntityType.FAMILY, families, filters)


class FiltersResource(BaseResource):
    def get(self, filters: list[Filter] | None = None):
        return self._client.get_entities(EntityType.FILTER, filters)

    def get_by_id(self, filter_id: int):
        return self._client.get_entity(EntityType.FILTER, filter_id)

    def update(
        self, filters_data: list[dict], query_filters: list[Filter] | None = None
    ):
        return self._client.update_entities(
            EntityType.FILTER, filters_data, query_filters
        )

    def create(
        self, filters_data: list[dict], query_filters: list[Filter] | None = None
    ):
        return self._client.create_entities(
            EntityType.FILTER, filters_data, query_filters
        )


class StoriesResource(BaseResource):
    def get(self, filters: list[Filter] | None = None):
        return self._client.get_entities(EntityType.STORY, filters)

    def get_by_id(self, story_id: int):
        return self._client.get_entity(EntityType.STORY, story_id)

    def update(self, stories: list[dict], filters: list[Filter] | None = None):
        return self._client.update_entities(EntityType.STORY, stories, filters)

    def create(self, stories: list[dict], filters: list[Filter] | None = None):
        return self._client.create_entities(EntityType.STORY, stories, filters)


class SpacesResource(BaseResource):
    def get(self, filters: list[Filter] | None = None):
        return self._client.get_entities(EntityType.SPACE, filters)

    def get_by_id(self, space_id: int):
        return self._client.get_entity(EntityType.SPACE, space_id)

    def update(self, spaces: list[dict], filters: list[Filter] | None = None):
        return self._client.update_entities(EntityType.SPACE, spaces, filters)

    def create(self, spaces: list[dict], filters: list[Filter] | None = None):
        return self._client.create_entities(EntityType.SPACE, spaces, filters)


class GroupsResource(BaseResource):
    def get(self, filters: list[Filter] | None = None):
        return self._client.get_entities(EntityType.GROUP, filters)

    def get_by_id(self, group_id: int):
        return self._client.get_entity(EntityType.GROUP, group_id)

    def update(self, groups: list[dict], filters: list[Filter] | None = None):
        return self._client.update_entities(EntityType.GROUP, groups, filters)

    def create(self, groups: list[dict], filters: list[Filter] | None = None):
        return self._client.create_entities(EntityType.GROUP, groups, filters)


class FairsResource(BaseResource):
    def get(self, filters: list[Filter] | None = None):
        return self._client.get_entities(EntityType.FAIR, filters)

    def get_by_id(self, fair_id: int):
        return self._client.get_entity(EntityType.FAIR, fair_id)

    def update(self, fairs: list[dict], filters: list[Filter] | None = None):
        return self._client.update_entities(EntityType.FAIR, fairs, filters)

    def create(self, fairs: list[dict], filters: list[Filter] | None = None):
        return self._client.create_entities(EntityType.FAIR, fairs, filters)
