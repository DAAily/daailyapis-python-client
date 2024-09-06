from daaily.enums import DaailyService, Environment
from daaily.http.client import Client as HttpClient
from daaily.http.models import HttpResponse
from daaily.http.utility import extract_response_data
from daaily.peggie.enums import PeggieEndpoint
from daaily.peggie.utility import gen_peggie_v1_endpoint_url


class Client:
    def __init__(self, environment: Environment = Environment.STAGING) -> None:
        # HTTP REQUESTS
        self.http_client = HttpClient()
        self.environment = environment

    async def make_predict_request(
        self, peggie_endpoint: PeggieEndpoint, data: dict | list
    ) -> HttpResponse:
        endpoint_url = gen_peggie_v1_endpoint_url(self.environment, peggie_endpoint)
        response = await self.http_client.post_request(endpoint_url, data, None)
        return extract_response_data(response, DaailyService.PEGGIE)
