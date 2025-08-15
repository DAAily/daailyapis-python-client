from typing import Any, Dict, Generator

from daaily.lucy.enums import EntityType, Service
from daaily.lucy.models import Filter

from .. import BaseResource


class JournalistsResource(BaseResource):
    def get(
        self, filters: list[Filter] | None = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Retrieves journalists with optional filtering, returning them as a generator
        that yields each journalist one at a time.

        Available filters:
            - journalist_ids (str): Filter by comma separated journalist IDs.

        Note that the following filters are automatically added to the query:
            - skip (int): Number of records to skip.
            - limit (int): Maximum number of records to retrieve.

        Args:
            filters (list[Filter] | None): A list of filters to apply to the query.

        Yields:
            dict: A dictionary representing a single journalist.

        Example:
            ```python
            # Define filters
            filters = [Filter("journalist_ids", "12345, 12322")]

            # Get journalists (pagination handled internally)
            journalists = client.journalists.get(filters=filters)

            # Iterate over the results without worrying about pagination
            for j in journalists:
                print(f"ID: {j['journalist_id']}, Name: {j['name']}")
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
            response = self._client.get_entities(EntityType.JOURNALIST, new_filters)
            if response.status != 200:
                break
            for item in response.json():  # type: ignore
                yield item
            skip_value = str(int(skip_value) + int(limit_value))
            skip_filter.value = skip_value
            new_filters = [f for f in new_filters if f.name != "skip"]
            new_filters.append(skip_filter)

    def get_by_id(self, journalist_id: int):
        return self._client.get_entity(EntityType.JOURNALIST, journalist_id)

    def update(
        self,
        journalists: list[dict],
        filters: list[Filter] | None = None,
        service: Service = Service.SPARKY,
    ):
        return self._client.update_entities(
            EntityType.JOURNALIST, journalists, filters, service=service
        )

    def create(
        self,
        journalists: list[dict],
        filters: list[Filter] | None = None,
        service: Service = Service.SPARKY,
    ):
        return self._client.create_entities(
            EntityType.JOURNALIST, journalists, filters, service=service
        )
