from daaily.enums import DaailyService, Environment
from daaily.http.client import Client as HttpClient
from daaily.http.enums import HttpAuthType
from daaily.http.models import HttpResponse
from daaily.http.utility import add_authorization_header, extract_response_data
from daaily.lucy.enums import LucyEndpoint, Status
from daaily.lucy.utility import (
    gen_graphql_entity_query,
    gen_graphql_payload_with_query,
    gen_lucy_graphql_endpoint_url,
    gen_lucy_v2_endpoint_url,
    gen_request_url_with_id,
    gen_request_url_with_params,
)
from daaily.sally.client import Client as SallyClient


class Client:
    def __init__(
        self,
        environment: Environment = Environment.STAGING,
        check_response_code: bool = True,
    ) -> None:
        # DAAILY AUTH
        self.sally_client = SallyClient()
        # HTTP REQUESTS
        self.http_client = HttpClient()
        self.environment = environment
        # BYPASS RESPONSE CODE CHECK
        self.check_response_code = check_response_code

    async def _gen_request_headers(self) -> dict:
        sally_id_token = await self.sally_client.get_token()
        headers = add_authorization_header(HttpAuthType.BEARER, sally_id_token, None)
        return headers

    async def get_entity(
        self, lucy_endpoint: LucyEndpoint, entity_id: int
    ) -> HttpResponse:
        endpoint_url = gen_lucy_v2_endpoint_url(self.environment, lucy_endpoint)
        request_url = gen_request_url_with_id(endpoint_url, entity_id)
        headers = await self._gen_request_headers()
        response = await self.http_client.get_request(request_url, headers)
        response = extract_response_data(
            response, DaailyService.LUCY, check_response_code=self.check_response_code
        )
        return response

    async def get_entities(
        self, lucy_endpoint: LucyEndpoint, params: dict
    ) -> HttpResponse:
        endpoint_url = gen_lucy_v2_endpoint_url(self.environment, lucy_endpoint)
        request_url = gen_request_url_with_params(endpoint_url, params)
        headers = await self._gen_request_headers()
        response = await self.http_client.get_request(request_url, headers)
        response = extract_response_data(
            response, DaailyService.LUCY, check_response_code=self.check_response_code
        )
        return response

    async def get_graphql_entities(
        self,
        lucy_endpoint: LucyEndpoint,
        fields: list,
        skip: int,
        limit: int,
        statuses: list[Status],
    ) -> HttpResponse:
        endpoint_url = gen_lucy_graphql_endpoint_url(self.environment, lucy_endpoint)
        query = gen_graphql_entity_query(lucy_endpoint, fields, skip, limit, statuses)
        payload = gen_graphql_payload_with_query(query)
        headers = await self._gen_request_headers()
        response = await self.http_client.post_request(endpoint_url, payload, headers)
        response = extract_response_data(
            response, DaailyService.LUCY, check_response_code=self.check_response_code
        )
        return response

    async def create_entities(
        self, lucy_endpoint: LucyEndpoint, params: dict, data: list[dict]
    ) -> HttpResponse:
        endpoint_url = gen_lucy_v2_endpoint_url(self.environment, lucy_endpoint)
        request_url = gen_request_url_with_params(endpoint_url, params)
        headers = await self._gen_request_headers()
        response = await self.http_client.post_request(request_url, data, headers)
        response = extract_response_data(
            response, DaailyService.LUCY, check_response_code=self.check_response_code
        )
        return response

    async def update_entities(
        self, lucy_endpoint: LucyEndpoint, params: dict, data: list[dict]
    ) -> HttpResponse:
        endpoint_url = gen_lucy_v2_endpoint_url(self.environment, lucy_endpoint)
        request_url = gen_request_url_with_params(endpoint_url, params)
        headers = await self._gen_request_headers()
        response = await self.http_client.put_request(request_url, data, headers)
        response = extract_response_data(
            response, DaailyService.LUCY, check_response_code=self.check_response_code
        )
        return response
