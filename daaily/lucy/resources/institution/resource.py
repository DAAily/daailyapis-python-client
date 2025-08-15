from typing import Any, Dict, Generator

from daaily.lucy.enums import EntityType, Service
from daaily.lucy.models import Filter

from .. import BaseResource


class InstitutionsResource(BaseResource):
    def get(
        self, filters: list[Filter] | None = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Retrieves institutions with optional filtering, returning them as a generator
        that yields each institution one at a time.

        Available filters:
            - institution_ids (str): Filter by comma separated institution IDs.

        Note that the following filters are automatically added to the query:
            - skip (int): Number of records to skip.
            - limit (int): Maximum number of records to retrieve.

        Args:
            filters (list[Filter] | None): A list of filters to apply to the query.

        Yields:
            dict: A dictionary representing a single institution.

        Example:
            ```python
            # Define filters
            filters = [Filter("institution_ids", "12345, 78910")]

            # Get institutions (pagination handled internally)
            institutions = client.institutions.get(filters=filters)

            # Iterate over the results without worrying about pagination
            for i in institutions:
                print(f"ID: {i['institution_id']}, Name: {i['name']}")
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
            response = self._client.get_entities(EntityType.INSTITUTION, new_filters)
            if response.status != 200:
                break
            for item in response.json():  # type: ignore
                yield item
            skip_value = str(int(skip_value) + int(limit_value))
            skip_filter.value = skip_value
            new_filters = [f for f in new_filters if f.name != "skip"]
            new_filters.append(skip_filter)

    def get_by_id(self, institution_id: int):
        return self._client.get_entity(EntityType.INSTITUTION, institution_id)

    def update(
        self,
        institutions: list[dict],
        filters: list[Filter] | None = None,
        service: Service = Service.SPARKY,
    ):
        return self._client.update_entities(
            EntityType.INSTITUTION, institutions, filters, service=service
        )

    def create(
        self,
        institutions: list[dict],
        filters: list[Filter] | None = None,
        service: Service = Service.SPARKY,
    ):
        return self._client.create_entities(
            EntityType.INSTITUTION, institutions, filters, service=service
        )
