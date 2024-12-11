import json

import daaily.transport
from daaily.credentials_sally import Credentials
from daaily.lucy.enums import EntityType
from daaily.lucy.models import Filter
from daaily.lucy.resources import (
    CollectionsResource,
    CreatorsResource,
    DistributorsResource,
    FairsResource,
    FamiliesResource,
    FiltersResource,
    GroupsResource,
    JournalistsResource,
    ManufacturersResource,
    MaterialsResource,
    ProductsResource,
    ProjectsResource,
    SpacesResource,
    StoriesResource,
)
from daaily.lucy.response import Response
from daaily.lucy.utils import (
    build_query_string,
    get_entity_endpoint,
    get_skip_query,
    handle_entity_response_data,
)
from daaily.transport.urllib3_http import AuthorizedHttp

LUCY_V2_BASE_URL = "https://lucy.daaily.com/api/v2"


class Client:
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
        self.manufacturers = ManufacturersResource(self)
        self.distributors = DistributorsResource(self)
        self.collections = CollectionsResource(self)
        self.journalists = JournalistsResource(self)
        self.materials = MaterialsResource(self)
        self.projects = ProjectsResource(self)
        self.products = ProductsResource(self)
        self.creators = CreatorsResource(self)
        self.families = FamiliesResource(self)
        self.filters = FiltersResource(self)
        self.stories = StoriesResource(self)
        self.spaces = SpacesResource(self)
        self.groups = GroupsResource(self)
        self.fairs = FairsResource(self)

    def _do_request(self, method, url, **kwargs) -> daaily.transport.Response:
        """
        Makes a request to the server.
        """
        r = self._auth_http.request(method, url, **kwargs)
        return r

    def get_entity(self, entity_type: EntityType, entity_id: int) -> Response:
        """
        Gets a entity of a certain type.
        """
        url = get_entity_endpoint(self._base_url, entity_type)
        entity_url = f"{url}/{entity_id}"
        return Response.from_response(self._do_request("GET", entity_url))

    def get_entities(
        self, entity_type: EntityType, filters: list[Filter] | None = None
    ) -> Response:
        """
        Gets all entities of a certain type.
        """
        url = get_entity_endpoint(self._base_url, entity_type)
        if filters is not None:
            url += build_query_string(filters)
        return Response.from_response(self._do_request("GET", url))

    def create_entities(
        self,
        entity_type: EntityType,
        entities: list[dict],
        filters: list[Filter] | None = None,
    ):
        """
        Creates entities of a certain type.
        """
        url = get_entity_endpoint(self._base_url, entity_type)
        if filters is not None:
            url += build_query_string(filters)
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
        url = get_entity_endpoint(self._base_url, entity_type)
        if filters is not None:
            url += build_query_string(filters)
        return self._do_request("PUT", url, json=entities)

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
            lskip, limit = get_skip_query(skip)
            skip_filter = Filter(name="skip", value=str(lskip))
            limit_filter = Filter(name="limit", value=str(limit))
            entity_filters = [skip_filter, limit_filter]
            if filters is not None:
                entity_filters.extend(filters)
            response = self.get_entities(entity_type, filters=entity_filters)
            entities, more_data = handle_entity_response_data(response, entities)
            skip += 1
            if not more_data:
                break
            if max_pages and skip >= max_pages:
                break
        return entities

    def upload_file(
        self,
        file_data: bytes,
        mime_type: str,
        endpoint: str,
        metadata: dict | None = None,
        short_uuid: str | None = None,
    ) -> str:
        """
        Uploads a file to the server.
        """
        headers = {"Content-Type": mime_type}
        if metadata:
            headers.update(metadata)
        file_upload_url = f"{self._base_url}/{endpoint}"
        request_method = "POST"
        if short_uuid:
            file_upload_url += f"/{short_uuid}"
            request_method = "PUT"
        resp = self._do_request(
            request_method, file_upload_url, body=file_data, headers=headers
        )
        if resp.status != 200:
            raise Exception(
                f"Failed to upload image. Status code: {resp.status}. {resp.data}"
            )
        response_data = json.loads(resp.data.decode("utf-8"))
        if "blob_id" not in response_data:
            raise Exception(f"Failed to get signed url: {response_data}")
        return response_data["blob_id"]
