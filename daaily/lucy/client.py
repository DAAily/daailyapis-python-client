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
        if r.status != 200:
            raise Exception(f"Request failed with status {r.status}")
        return r

    def _get_entity_endpoint(self, entity_type: EntityType):
        return f"{self._base_url}/{entity_type_endpoint_mapping[entity_type]}"

    def _build_query_string(self, filters: list[Filter]):
        query_string = "?"
        for filter in filters:
            query_string += f"{filter.name}={filter.value}&"
        return query_string

    def get_entities(
        self,
        entity_type: EntityType,
        filters: list[Filter] | None = None,
        limit=100,
        disable_pagination=False,
    ):
        """
        Gets all entities of a certain type.
        """
        url = self._get_entity_endpoint(entity_type)
        if filters is not None:
            url += self._build_query_string(filters)
        return self._do_request("GET", url)
