import json

import daaily.lucy
from daaily.credentials_sally import Credentials
from daaily.lucy.config import entity_type_endpoint_mapping
from daaily.lucy.enums import EntityType
from daaily.lucy.models import Filter
from daaily.transport import Response
from daaily.transport.urllib3_http import AuthorizedHttp

LUCY_V2_BASE_URL = "https://lucy.daaily.com/api/v2"


class Client(daaily.lucy.Client):
    """
    The Lucy client is used to interact with the Lucy server.
    It provides functionality in order to make requests to each of Lucy's endpoints
    including the ability to create, update, and delete objects.
    You will also be able to specify to either use the client in a synchronous or
    asynchronous manner.
    """

    def __init__(
        self,
        credentials: Credentials | None = None,
        http=None,
        base_url: str | None = None,
    ):
        """
        Creates a new Lucy client.
        """
        if credentials is None:
            credentials = Credentials()
        self._credentials = credentials
        if base_url is None:
            base_url = LUCY_V2_BASE_URL
        self._base_url = base_url
        if http is not None:
            """
            TODO: Add custom request handlers. That allows async requests.
            Needs to follow the same interface as the http_client. By implementing
            abc classes.
            """
            raise NotImplementedError("Custom request handlers are not supported yet.")
        self._auth_http = AuthorizedHttp(self._credentials)

    def _do_request(self, method, url, **kwargs) -> Response:
        """
        Makes a request to the server.
        """
        r = self._auth_http.request(method, url, **kwargs)
        return r

    def _get_entity_endpoint(self, entity_type: EntityType):
        return f"{self._base_url}/{entity_type_endpoint_mapping[entity_type]}"

    def _build_query_string(self, filters: list[Filter]):
        query_string = "?"
        for filter in filters:
            query_string += f"{filter.name}={filter.value}&"
        return query_string

    def get_skip_query(self, skip: int) -> tuple[int, int]:
        limit = 500
        lskip = limit * skip
        return lskip, limit

    def handle_entity_response_data(
        self, response: Response, entities: list[dict]
    ) -> tuple[list[dict], bool]:
        if response.status == 200:
            data = json.loads(response.data.decode("utf-8"))
            entities.extend(data)
            more_data = True
        else:
            more_data = False
        return entities, more_data

    def get_entity(self, entity_type: EntityType, entity_id: int):
        """
        Gets a entity of a certain type.
        """
        url = self._get_entity_endpoint(entity_type)
        entity_url = f"{url}/{entity_id}"
        return self._do_request("GET", entity_url)

    def get_entities(
        self, entity_type: EntityType, filters: list[Filter] | None = None
    ):
        """
        Gets all entities of a certain type.
        """
        url = self._get_entity_endpoint(entity_type)
        if filters is not None:
            url += self._build_query_string(filters)
        return self._do_request("GET", url)

    def create_entities(
        self,
        entity_type: EntityType,
        entities: list[dict],
        filters: list[Filter] | None = None,
    ):
        """
        Creates entities of a certain type.
        """
        url = self._get_entity_endpoint(entity_type)
        if filters is not None:
            url += self._build_query_string(filters)
        return self._do_request("POST", url, json=entities)

    def update_entities(
        self,
        entity_type: EntityType,
        entities: list[dict],
        filters: list[Filter] | None = None,
    ):
        """
        Updates entities of a certain type.
        """
        url = self._get_entity_endpoint(entity_type)
        if filters is not None:
            url += self._build_query_string(filters)
        return self._do_request("PUT", url, json=entities)

    # Utility functions to get all entities via pagination of a certain type

    def get_paginated_entities(
        self,
        entity_type: EntityType,
        filters: list[Filter] | None = None,
        max_pages: int | None = None,
    ) -> list[dict]:
        """
        This function is used to get all entities of a certain type while using
        pagination for bulk retrieval. The function will fetch entities in batches
        of 500 until all entities have been retrieved or until the max_pages limit
        has been reached.

        DO NOT provide filters for SKIP and LIMIT as they will be
        automatically added by the function!
        """
        skip = 0
        more_data = True
        entities = []
        while more_data:
            lskip, limit = self.get_skip_query(skip)
            skip_filter = Filter(name="skip", value=str(lskip))
            limit_filter = Filter(name="limit", value=str(limit))
            entity_filters = [skip_filter, limit_filter]
            if filters is not None:
                entity_filters.extend(filters)
            response = self.get_entities(entity_type, filters=entity_filters)
            entities, more_data = self.handle_entity_response_data(response, entities)
            skip += 1
            if not more_data:
                break
            if max_pages and skip >= max_pages:
                break
        return entities

    # Utility functions to get a single entity of a certain type

    def get_manufacturer(self, manufacturer_id: int):
        return self.get_entity(EntityType.MANUFACTURER, manufacturer_id)

    def get_distributor(self, distributor_id: int):
        return self.get_entity(EntityType.DISTRIBUTOR, distributor_id)

    def get_collection(self, collection_id: int):
        return self.get_entity(EntityType.COLLECTION, collection_id)

    def get_journalist(self, journalist_id: int):
        return self.get_entity(EntityType.JOURNALIST, journalist_id)

    def get_material(self, material_id: int):
        return self.get_entity(EntityType.MATERIAL, material_id)

    def get_project(self, project_id: int):
        return self.get_entity(EntityType.PROJECT, project_id)

    def get_product(self, product_id: int):
        return self.get_entity(EntityType.PRODUCT, product_id)

    def get_creator(self, creator_id: int):
        return self.get_entity(EntityType.CREATOR, creator_id)

    def get_family(self, family_id: int):
        return self.get_entity(EntityType.FAMILY, family_id)

    def get_filter(self, filter_id: int):
        return self.get_entity(EntityType.FILTER, filter_id)

    def get_story(self, story_id: int):
        return self.get_entity(EntityType.STORY, story_id)

    def get_space(self, space_id: int):
        return self.get_entity(EntityType.SPACE, space_id)

    def get_group(self, group_id: int):
        return self.get_entity(EntityType.GROUP, group_id)

    def get_fair(self, fair_id: int):
        return self.get_entity(EntityType.FAIR, fair_id)

    # Utility functions to get all entities of a certain type

    def get_manufacturers(self, filters: list[Filter] | None = None):
        return self.get_entities(EntityType.MANUFACTURER, filters)

    def get_distributors(self, filters: list[Filter] | None = None):
        return self.get_entities(EntityType.DISTRIBUTOR, filters)

    def get_collections(self, filters: list[Filter] | None = None):
        return self.get_entities(EntityType.COLLECTION, filters)

    def get_journalists(self, filters: list[Filter] | None = None):
        return self.get_entities(EntityType.JOURNALIST, filters)

    def get_materials(self, filters: list[Filter] | None = None):
        return self.get_entities(EntityType.MATERIAL, filters)

    def get_projects(self, filters: list[Filter] | None = None):
        return self.get_entities(EntityType.PROJECT, filters)

    def get_products(self, filters: list[Filter] | None = None):
        return self.get_entities(EntityType.PRODUCT, filters)

    def get_creators(self, filters: list[Filter] | None = None):
        return self.get_entities(EntityType.CREATOR, filters)

    def get_families(self, filters: list[Filter] | None = None):
        return self.get_entities(EntityType.FAMILY, filters)

    def get_filters(self, filters: list[Filter] | None = None):
        return self.get_entities(EntityType.FILTER, filters)

    def get_stories(self, filters: list[Filter] | None = None):
        return self.get_entities(EntityType.STORY, filters)

    def get_spaces(self, filters: list[Filter] | None = None):
        return self.get_entities(EntityType.SPACE, filters)

    def get_groups(self, filters: list[Filter] | None = None):
        return self.get_entities(EntityType.GROUP, filters)

    def get_fairs(self, filters: list[Filter] | None = None):
        return self.get_entities(EntityType.FAIR, filters)

    # Utility functions to create entities of a certain type

    def create_manufacturers(
        self, manufacturers: list[dict], filters: list[Filter] | None = None
    ):
        return self.create_entities(EntityType.MANUFACTURER, manufacturers, filters)

    def create_distributors(
        self, distributors: list[dict], filters: list[Filter] | None = None
    ):
        return self.create_entities(EntityType.DISTRIBUTOR, distributors, filters)

    def create_collections(
        self, collections: list[dict], filters: list[Filter] | None = None
    ):
        return self.create_entities(EntityType.COLLECTION, collections, filters)

    def create_journalists(
        self, journalists: list[dict], filters: list[Filter] | None = None
    ):
        return self.create_entities(EntityType.JOURNALIST, journalists, filters)

    def create_materials(
        self, materials: list[dict], filters: list[Filter] | None = None
    ):
        return self.create_entities(EntityType.MATERIAL, materials, filters)

    def create_projects(
        self, projects: list[dict], filters: list[Filter] | None = None
    ):
        return self.create_entities(EntityType.PROJECT, projects, filters)

    def create_products(
        self, products: list[dict], filters: list[Filter] | None = None
    ):
        return self.create_entities(EntityType.PRODUCT, products, filters)

    def create_creators(
        self, creators: list[dict], filters: list[Filter] | None = None
    ):
        return self.create_entities(EntityType.CREATOR, creators, filters)

    def create_families(
        self, families: list[dict], filters: list[Filter] | None = None
    ):
        return self.create_entities(EntityType.FAMILY, families, filters)

    def create_filters(
        self, filters: list[dict], query_filters: list[Filter] | None = None
    ):
        return self.create_entities(EntityType.FILTER, filters, query_filters)

    def create_stories(self, stories: list[dict], filters: list[Filter] | None = None):
        return self.create_entities(EntityType.STORY, stories, filters)

    def create_spaces(self, spaces: list[dict], filters: list[Filter] | None = None):
        return self.create_entities(EntityType.SPACE, spaces, filters)

    def create_groups(self, groups: list[dict], filters: list[Filter] | None = None):
        return self.create_entities(EntityType.GROUP, groups, filters)

    def create_fairs(self, fairs: list[dict], filters: list[Filter] | None = None):
        return self.create_entities(EntityType.FAIR, fairs, filters)

    # Utility functions to update entities of a certain type

    def update_manufacturers(
        self, manufacturers: list[dict], filters: list[Filter] | None = None
    ):
        return self.update_entities(EntityType.MANUFACTURER, manufacturers, filters)

    def update_distributors(
        self, distributors: list[dict], filters: list[Filter] | None = None
    ):
        return self.update_entities(EntityType.DISTRIBUTOR, distributors, filters)

    def update_collections(
        self, collections: list[dict], filters: list[Filter] | None = None
    ):
        return self.update_entities(EntityType.COLLECTION, collections, filters)

    def update_journalists(
        self, journalists: list[dict], filters: list[Filter] | None = None
    ):
        return self.update_entities(EntityType.JOURNALIST, journalists, filters)

    def update_materials(
        self, materials: list[dict], filters: list[Filter] | None = None
    ):
        return self.update_entities(EntityType.MATERIAL, materials, filters)

    def update_projects(
        self, projects: list[dict], filters: list[Filter] | None = None
    ):
        return self.update_entities(EntityType.PROJECT, projects, filters)

    def update_products(
        self, products: list[dict], filters: list[Filter] | None = None
    ):
        return self.update_entities(EntityType.PRODUCT, products, filters)

    def update_creators(
        self, creators: list[dict], filters: list[Filter] | None = None
    ):
        return self.update_entities(EntityType.CREATOR, creators, filters)

    def update_families(
        self, families: list[dict], filters: list[Filter] | None = None
    ):
        return self.update_entities(EntityType.FAMILY, families, filters)

    def update_filters(
        self, filters: list[dict], query_filters: list[Filter] | None = None
    ):
        return self.update_entities(EntityType.FILTER, filters, query_filters)

    def update_stories(self, stories: list[dict], filters: list[Filter] | None = None):
        return self.update_entities(EntityType.STORY, stories, filters)

    def update_spaces(self, spaces: list[dict], filters: list[Filter] | None = None):
        return self.update_entities(EntityType.SPACE, spaces, filters)

    def update_groups(self, groups: list[dict], filters: list[Filter] | None = None):
        return self.update_entities(EntityType.GROUP, groups, filters)

    def update_fairs(self, fairs: list[dict], filters: list[Filter] | None = None):
        return self.update_entities(EntityType.FAIR, fairs, filters)
