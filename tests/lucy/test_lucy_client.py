import http.client as http_client
import unittest.mock as mock

import urllib3

import daaily.credentials
import daaily.credentials_sally
import daaily.lucy.client
import daaily.lucy.utils
import daaily.transport.urllib3_http
import tests.fixtures as fixtures


class CredentialsStub(daaily.credentials_sally.Credentials):
    def __init__(self, id_token="token"):
        self.id_token = id_token

    def apply(self, headers, id_token=None):
        headers["authorization"] = self.id_token

    def before_request(self, request, headers):
        self.apply(headers)


class TestLucyClient:
    def test_constructor(self):
        base_url = mock.sentinel.base_url
        credentials = mock.create_autospec(
            daaily.credentials.Credentials, instance=True
        )
        client = daaily.lucy.client.Client(credentials=credentials, base_url=base_url)
        assert client._base_url == mock.sentinel.base_url
        assert client._credentials == credentials

    def test_get_entity_endpoint(self):
        credentials = CredentialsStub()
        lucy = daaily.lucy.client.Client(credentials=credentials)
        endpoint = daaily.lucy.utils.get_entity_endpoint(lucy._base_url, "product")  # type: ignore
        assert endpoint == "https://lucy.daaily.com/api/v2/products"


class TestRequestResponse(fixtures.RequestResponseTests):
    def make_request(self):
        http = urllib3.PoolManager()
        return daaily.transport.urllib3_http.Request(http)

    def test_http(self, server):
        credentials = CredentialsStub()
        lucy = daaily.lucy.client.Client(credentials=credentials, base_url=server.url)
        response = lucy.get_entities("product")  # type: ignore
        assert response.status == http_client.OK
        assert response.headers["authorization"] == "token"
        assert response.data == b"Lucy Products"
