import http.client as http_client
import urllib3

from unittest import mock

import daaily.transport.urllib3_http
import daaily.transport.exceptions

from tests.transport import fixtures
import daaily.credentials_sally
import daaily.credentials


class TestRequestResponse(fixtures.RequestResponseTests):
    def make_request(self):
        return daaily.transport.urllib3_http.Request()

    def test_http(self, server):
        request = self.make_request()
        request.http
        response = request(url=f"{server.url}/basic", method="GET")
        assert response.status == http_client.OK
        assert response.headers["x-test-header"] == "value"
        assert response.data == b"Basic Content"


class CredentialsStub(daaily.credentials.Credentials):
    def __init__(self, token="token"):
        super(CredentialsStub, self).__init__()
        self.token = token

    def apply(self, headers, token=None):
        headers["authorization"] = self.token

    def before_request(self, request, headers):
        self.apply(headers)

    def refresh(self, request):
        self.token += "1"


class HttpStub:
    def __init__(self, responses, headers=None):
        self.responses = responses
        self.requests = []
        self.headers = headers or {}

    def urlopen(self, method, url, body=None, headers=None, **kwargs):
        self.requests.append((method, url, body, headers, kwargs))
        return self.responses.pop(0)


class ResponseStub:
    def __init__(self, status=http_client.OK, data=None):
        self.status = status
        self.data = data


class TestAuthorizedHttp:
    TEST_URL = "http://example.com"

    def test_auth_http_defaults(self):
        auth_http = daaily.transport.urllib3_http.AuthorizedHttp(
            mock.sentinel.credentials
        )
        assert auth_http.credentials == mock.sentinel.credentials
        assert isinstance(auth_http.http, urllib3.PoolManager)

    def test_urlopen_no_refresh(self):
        credentials = mock.Mock(wraps=CredentialsStub())
        response = ResponseStub()
        http = HttpStub([response])
        auth_http = daaily.transport.urllib3_http.AuthorizedHttp(credentials, http=http)
        result = auth_http.urlopen("GET", self.TEST_URL)
        assert result == response
        assert credentials.before_request.called
        assert not credentials.refresh.called
        assert http.requests == [
            ("GET", self.TEST_URL, None, {"authorization": "token"}, {})
        ]

    def test_urlopen_refresh(self):
        credentials = mock.Mock(wraps=CredentialsStub())
        final_response = ResponseStub(status=http_client.OK)
        # First request will 401, second request will succeed.
        http = HttpStub([ResponseStub(status=http_client.UNAUTHORIZED), final_response])
        auth_http = daaily.transport.urllib3_http.AuthorizedHttp(credentials, http=http)
        auth_http = auth_http.urlopen("GET", "http://example.com")
        assert auth_http == final_response
        assert credentials.before_request.call_count == 2
        assert credentials.refresh.called
        assert http.requests == [
            ("GET", self.TEST_URL, None, {"authorization": "token"}, {}),
            ("GET", self.TEST_URL, None, {"authorization": "token1"}, {}),
        ]
