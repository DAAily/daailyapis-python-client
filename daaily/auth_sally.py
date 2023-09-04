import http.client as http_client
import json
import os
from urllib import parse

import daaily.credentials
import daaily.transport.exceptions
from daaily.exceptions import MissingEnvironmentVariable

REFRESH_THRESHOLD_SECS = 600
DAAILY_USER_EMAIL_ENV = "DAAILY_USER_EMAIL"
DAAILY_USER_UID_ENV = "DAAILY_USER_UID"
DAAILY_API_KEY_ENV = "DAAILY_API_KEY"
MISSING_ENV_USER_CREDENTIALS_MESSAGE = (
    "You either have to pass the user credentials are set them via the environment."
)
SALLY_BASE_URL = "https://sally.daaily.com/api/v2"
TOKEN_ENDPOINT = "tokens/get-token"
REFRESH_ENDPOINT = "tokens/get-token-with-refresh-token"


class Credentials(daaily.credentials.Credentials):
    """
    The Lucy client is used to interact with the Lucy server.
    It provides functionality in order to make requests to each of Lucy's endpoints
    including the ability to create, update, and delete objects.
    You will also be able to specify to either use the client in a synchronous or
    asynchronous manner.
    """

    def __init__(
        self,
        user_email: str | None = None,
        user_uid: str | None = None,
        api_key: str | None = None,
    ):
        """
        Initializes authentication that is required for Daaily clients.
        """
        super(Credentials, self).__init__()
        if user_email is None or user_uid is None or api_key is None:
            try:
                user_email = os.environ["DAAILY_USER_EMAIL"]
                user_uid = os.environ["DAAILY_USER_UID"]
                api_key = os.environ["DAAILY_API_KEY"]
            except KeyError as e:
                raise MissingEnvironmentVariable(
                    f"{MISSING_ENV_USER_CREDENTIALS_MESSAGE}\nError: {str(e.args)}"
                ) from e
        self._user_email = user_email
        self._user_uid = user_uid
        self._api_key = api_key

    def _make_request(self, request, headers, request_body):
        response = request(
            url=self._token_exchange_endpoint,
            method="POST",
            headers=headers,
            body=parse.urlencode(request_body).encode("utf-8"),
        )
        if response.status != http_client.OK:
            raise daaily.transport.exceptions.TransportException(
                f"Request failed with status code {response.status}."
            )
        response_body = (
            response.data.decode("utf-8")
            if hasattr(response.data, "decode")
            else response.data
        )
        response_data = json.loads(response_body)
        return response_data

    def refresh(self, request):
        if self._id_token and self._refresh_token:
            return self.refresh_token(request, self._refresh_token)
        else:
            return self.get_token(request)

    def get_token(self, request):
        """Exchanges a refresh token for an access token based on the
        RFC6749 spec.

        Args:
            request (google.auth.transport.Request): A callable used to make
                HTTP requests.
            subject_token (str): The OAuth 2.0 refresh token.
        """
        self._token_exchange_endpoint = f"{SALLY_BASE_URL}/{TOKEN_ENDPOINT}"
        return self._make_request(
            request,
            None,
            {"email": f"{self._user_email}", "user_uid": f"{self._user_uid}"},
        )

    def refresh_token(self, request, refresh_token: str):
        """Exchanges a refresh token for an access token based on the
        RFC6749 spec.

        Args:
            request (google.auth.transport.Request): A callable used to make
                HTTP requests.
            subject_token (str): The OAuth 2.0 refresh token.
        """
        self._token_exchange_endpoint = (
            f"{SALLY_BASE_URL}/{REFRESH_ENDPOINT}&key={self._api_key}"
        )
        return self._make_request(
            request,
            None,
            {"email": f"{self._user_email}", "refresh_token": refresh_token},
        )

    # def _update_credentials(self, out):
    #     """
    #     Updates the credentials for the client.
    #     """
    #     pass

    # def apply_to_header(self, headers: dict, id_token=None):
    #     """Apply the token to the authentication header.

    #     Args:
    #         headers (Mapping): The HTTP request headers.
    #         id_token (Optional[str]): If specified, overrides the current id token.
    #     """
    #     headers["authorization"] = f"Bearer {id_token or self._id_token}"

    # def refresh(self, request):
    #     pass

    # def before_request(self, request, headers):
    #     """Performs credential-specific before request logic.

    #     Refreshes the credentials if necessary, then calls :meth:`apply_to_header` to
    #     apply the token to the authentication header.
    #     """
    #     if not self.valid:
    #         self.refresh(request)
    #     self.apply_to_header(headers)
