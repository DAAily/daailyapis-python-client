import json

from urllib3 import filepost

import daaily.transport
from daaily.credentials_sally import Credentials
from daaily.lucy.constants import LUCY_V2_BASE_URL_PRODUCTION
from daaily.lucy.enums import EntityType
from daaily.lucy.models import Filter
from daaily.lucy.resources.collection import CollectionsResource
from daaily.lucy.resources.creator import CreatorsResource
from daaily.lucy.resources.distributor import DistributorsResource
from daaily.lucy.resources.fair import FairsResource
from daaily.lucy.resources.family import FamiliesResource
from daaily.lucy.resources.file import FilesResource
from daaily.lucy.resources.filter import FiltersResource
from daaily.lucy.resources.group import GroupsResource
from daaily.lucy.resources.journalist import JournalistsResource
from daaily.lucy.resources.manufacturer import ManufacturersResource
from daaily.lucy.resources.material import MaterialsResource
from daaily.lucy.resources.product import ProductsResource
from daaily.lucy.resources.project import ProjectsResource
from daaily.lucy.resources.space import SpacesResource
from daaily.lucy.resources.story import StoriesResource
from daaily.lucy.response import Response
from daaily.lucy.utils import (
    add_x_goog_metadata_to_headers,
    build_query_string,
    get_entity_endpoint,
    get_skip_query,
    handle_entity_response_data,
)
from daaily.transport.urllib3_http import AuthorizedHttp


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
            base_url = LUCY_V2_BASE_URL_PRODUCTION
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
        self.files = FilesResource(self)

    def _do_request(
        self, method, url, body=None, fields=None, headers=None, json=None, **kwargs
    ) -> daaily.transport.Response:
        """
        Makes a request to the server.
        """
        r = self._auth_http.request(
            method, url, headers=headers, body=body, fields=fields, json=json, **kwargs
        )
        return r

    def get_entity(self, entity_type: EntityType, entity_id: int) -> Response:
        """
        Gets a entity of a certain type.
        """
        url = get_entity_endpoint(self._base_url, entity_type)
        entity_url = f"{url}/{entity_id}"
        return Response.from_response(self._do_request("GET", entity_url))

    def get_entity_custom(
        self, entity_type: EntityType, identifier: str, identifier_field: str
    ) -> Response:
        """
        Gets a entity of a certain type.
        """
        url = get_entity_endpoint(self._base_url, entity_type)
        entity_url = f"{url}/{identifier_field}/{identifier}"
        return Response.from_response(self._do_request("GET", entity_url))

    def get_entity_audits(
        self,
        entity_type: EntityType,
        entity_id: int,
        filters: list[Filter] | None = None,
    ) -> Response:
        """
        Gets a entity audits of a certain entity type.
        """
        url = get_entity_endpoint(self._base_url, entity_type)
        entity_url = f"{url}/{entity_id}/audits"
        if filters is not None:
            entity_url += build_query_string(filters)
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
    ) -> Response:
        """
        Creates entities of a certain type.
        """
        url = get_entity_endpoint(self._base_url, entity_type)
        if filters is not None:
            url += build_query_string(filters)
        return Response.from_response(self._do_request("POST", url, json=entities))

    def update_entity(self, entity_type: EntityType, entity: dict) -> Response:
        """
        Updates a entity of a certain type.
        """
        url = get_entity_endpoint(self._base_url, entity_type)
        response = self._do_request("PUT", url, json=[entity])
        return Response.from_response(response, single_entity=True)

    def update_entities(
        self,
        entity_type: EntityType,
        entities: list[dict],
        filters: list[Filter] | None = None,
    ) -> Response:
        """
        Updates entities of a certain type.
        """
        url = get_entity_endpoint(self._base_url, entity_type)
        if filters is not None:
            url += build_query_string(filters)
        return Response.from_response(self._do_request("PUT", url, json=entities))

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
        file_name: str,
        mime_type: str,
        endpoint: str,
        metadata: dict | None = None,
        short_uuid: str | None = None,
    ) -> str:
        """
        Uploads a file to the server.
        """
        file_upload_url = f"{self._base_url}/{endpoint}"
        request_method = "POST"
        if short_uuid:
            file_upload_url += f"/{short_uuid}"
            request_method = "PUT"
        fields = {"file": (file_name, file_data, mime_type)}
        encoded_data, content_type = filepost.encode_multipart_formdata(fields)
        headers = {"Content-Type": content_type}
        if metadata:
            metadata_header_ready = add_x_goog_metadata_to_headers(metadata)
            headers.update(metadata_header_ready)
        resp = self._do_request(
            request_method,
            file_upload_url,
            body=encoded_data,
            headers=headers,
            encode_multipart=True,
        )
        if resp.status != 200:
            raise Exception(
                f"Failed to upload image. Status code: {resp.status}. {resp.data}"
            )
        response_data = json.loads(resp.data.decode("utf-8"))
        if "blob_id" not in response_data:
            raise Exception(f"Failed to get signed url: {response_data}")
        return response_data["blob_id"]
