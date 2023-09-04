from http import client as http_client

from daaily.auth_sally import Credentials
from daaily.transport.urllib3_http import AuthorizedHttp, Request

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
        self.credentials = credentials
        self.headers = {}
        self.body = None
        if base_url is None:
            base_url = LUCY_V2_BASE_URL
        self.base_url = base_url
        if http is not None:
            """
            TODO: Add custom request handlers. That allows async requests.
            Needs to follow the same interface as the http_client. By implementing
            abc classes.
            """
            raise NotImplementedError("Custom request handlers are not supported yet.")
        if http is None:
            http = Request()
        self.http = http
        self._auth_http = AuthorizedHttp(self.credentials, self.http)

    def _do_request(self, method, url, **kwargs) -> http_client.HTTPResponse:
        """
        Makes a request to the server.
        """
        # self.credentials.before_request(self.headers)
        r = self._auth_http.request(method, url, **kwargs)
        if r.status != 200:
            raise Exception(f"Request failed with status {r.status}")
        return r

    def get_entities_by_type(self, entity_type: str):
        """
        Gets all entities of a certain type.
        """
        url = f"{self.base_url}/{entity_type}"
        return self._do_request("GET", url)
