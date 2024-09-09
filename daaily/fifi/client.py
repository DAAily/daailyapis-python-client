import base64

from daaily.enums import DaailyService, Environment
from daaily.fifi.enums import FifiEndpoint, FifiProcessType
from daaily.fifi.utility import gen_fifi_endpoint_url, load_auth_env_values
from daaily.http.client import Client as HttpClient
from daaily.http.enums import HttpAuthType
from daaily.http.models import HttpResponse
from daaily.http.utility import add_authorization_header, extract_response_data


class Client:
    def __init__(self, environment: Environment = Environment.STAGING) -> None:
        # ENV FIFI CREDENTIALS
        auth_username, auth_password = load_auth_env_values()
        self.auth_username = auth_username
        self.auth_password = auth_password
        # HTTP REQUESTS
        self.http_client = HttpClient()
        self.environment = environment

    def _gen_request_headers(self) -> dict:
        credentials = f"{self.auth_username}:{self.auth_password}"
        auth_token = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
        headers = add_authorization_header(HttpAuthType.BASIC, auth_token, None)
        return headers

    async def make_extract_request(
        self,
        fifi_endpoint: FifiEndpoint,
        fifi_process_type: FifiProcessType,
        data: list[dict] | dict,
    ) -> HttpResponse:
        endpoint_url = gen_fifi_endpoint_url(
            self.environment, fifi_process_type, fifi_endpoint
        )
        headers = self._gen_request_headers()
        response = await self.http_client.post_request(endpoint_url, data, headers)
        return extract_response_data(response, DaailyService.FIFI)
