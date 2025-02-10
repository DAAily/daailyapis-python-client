from typing import Any, Dict, Generator

from daaily.lucy.enums import EntityType
from daaily.lucy.models import Filter

from . import BaseResource


class FamiliesResource(BaseResource):
    def get(
        self, filters: list[Filter] | None = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Retrieves families with optional filtering, returning them as a generator
        that yields each family one at a time.

        Available filters:
            - family_ids (str): Filter by comma separated family IDs.

        Note that the following filters are automatically added to the query:
            - skip (int): Number of records to skip.
            - limit (int): Maximum number of records to retrieve.

        Args:
            filters (list[Filter] | None): A list of filters to apply to the query.

        Yields:
            dict: A dictionary representing a single family.

        Example:
            ```python
            # Define filters
            filters = [Filter("family_ids", "12345, 78910")]

            # Get families (pagination handled internally)
            families = client.families.get(filters=filters)

            # Iterate over the results without worrying about pagination
            for f in families:
                print(f"ID: {f['family_id']}, Name: {f['name_en']}")
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
            response = self._client.get_entities(EntityType.FAMILY, filters)
            if response.status != 200:
                break
            for item in response.json():  # type: ignore
                yield item
            skip = int(skip_filter.value) + int(limit_filter.value)
            skip_filter.value = str(skip)
            filters = [f for f in filters if f.name != "skip"]
            filters.append(skip_filter)

    def get_by_id(self, family_id: int):
        return self._client.get_entity(EntityType.FAMILY, family_id)

    def update(self, families: list[dict], filters: list[Filter] | None = None):
        return self._client.update_entities(EntityType.FAMILY, families, filters)

    def create(self, families: list[dict], filters: list[Filter] | None = None):
        return self._client.create_entities(EntityType.FAMILY, families, filters)
