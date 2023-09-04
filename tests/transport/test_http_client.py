import pytest  # type: ignore
import http.client as http_client

from unittest import mock

import daaily.transport.urllib3_http
import daaily.transport.exceptions

from tests.transport import fixtures
import daaily.auth_sally


class TestRequestResponse(fixtures.RequestResponseTests):
    def make_request(self):
        return daaily.transport.urllib3_http.Request()

    def test_http(self, server):
        request = self.make_request()
        request.http
        response = request(url=f"{server.url}/basic", method="GET")

        # with pytest.raises(daaily.transport.exceptions.TransportException) as ex:
        #     request(url="https://{}".format(fixtures.NXDOMAIN), method="GET")
        assert response.status == http_client.OK
        assert response.headers["x-test-header"] == "value"
        assert response.data == b"Basic Content"
        # assert ex.match("https")

    def make_auth_http(self, server):
        """
        This tests first mocks the credentials class from daaily.auth_sally and then uses
        the mock to create an AuthorizedHttp object.
        """
        # credentials = daaily.auth_sally.Credentials()
        with mock.MagicMock() as mock_credentials:
            mock_credentials.before_request.return_value = None
            mock_credentials.id_token.return_value = "this-is-an-id-token"
            mock_credentials.refresh_token.return_value = "this-is-a-refresh-token"
        #     mock_credentials.id_token.return_value = "this-is-an-id-token"
        # mock_credentials.get_token.return_value = None
        # mock_credentials.refresh_token.return_value = None
        # mock_credentials._make_request.return_value = None
        # mock_credentials._token_exchange_endpoint = (
        #     f"{daaily.auth_sally.SALLY_BASE_URL}/{daaily.auth_sally.TOKEN_ENDPOINT}"
        # )
        # return daaily.transport.urllib3_http.AuthorizedHttp(mock_credentials)
        with mock.patch.object(credentials, "before_request", return_value=None):
            return daaily.transport.urllib3_http.AuthorizedHttp(credentials)
        auth_request = daaily.transport.urllib3_http.AuthorizedHttp(credentials)
        response = auth_request.request(
            url=f"{server.url}/make-auth-request", method="POST"
        )
        assert response.status == http_client.OK
        assert response.headers["Authentication"] == "Bearer"
        assert response.data == b"Authorized Content"
