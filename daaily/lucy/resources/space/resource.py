from typing import Any, Dict, Generator

from daaily.lucy.enums import EntityType, Service
from daaily.lucy.models import Filter

from .. import BaseResource


class SpacesResource(BaseResource):
    def get(
        self, filters: list[Filter] | None = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Retrieves spaces with optional filtering, returning them as a generator
        that yields each space one at a time.

        Available filters:
            - space_ids (str): Filter by comma separated space IDs.

        Note that the following filters are automatically added to the query:
            - skip (int): Number of records to skip.
            - limit (int): Maximum number of records to retrieve.

        Args:
            filters (list[Filter] | None): A list of filters to apply to the query.

        Yields:
            dict: A dictionary representing a single space.

        Example:
            ```python
            # Define filters
            filters = [Filter("space_ids", "12345, 78910")]

            # Get spaces (pagination handled internally)
            spaces = client.spaces.get(filters=filters)

            # Iterate over the results without worrying about pagination
            for s in spaces:
                print(f"ID: {s['space_id']}, Space Type: {s['space_type']}")
            ```
        """
        if filters is None:
            filters = []
        limit_value = "100"
        skip_value = "0"
        new_filters = []
        for f in filters:
            if f.name == "limit":
                limit_value = f.value
            elif f.name == "skip":
                skip_value = f.value
            else:
                new_filters.append(f)
        limit_filter = Filter(name="limit", value=limit_value)
        skip_filter = Filter(name="skip", value=skip_value)
        new_filters.append(limit_filter)
        new_filters.append(skip_filter)
        while True:
            response = self._client.get_entities(EntityType.SPACE, new_filters)
            if response.status != 200:
                break
            for item in response.json():  # type: ignore
                yield item
            skip_value = str(int(skip_value) + int(limit_value))
            skip_filter.value = skip_value
            new_filters = [f for f in new_filters if f.name != "skip"]
            new_filters.append(skip_filter)

    def get_by_id(self, space_id: int):
        return self._client.get_entity(EntityType.SPACE, space_id)

    def update(
        self,
        spaces: list[dict],
        filters: list[Filter] | None = None,
        service: Service = Service.SPARKY,
    ):
        return self._client.update_entities(
            EntityType.SPACE, spaces, filters, service=service
        )

    def create(
        self,
        spaces: list[dict],
        filters: list[Filter] | None = None,
        service: Service = Service.SPARKY,
    ):
        return self._client.create_entities(
            EntityType.SPACE, spaces, filters, service=service
        )
