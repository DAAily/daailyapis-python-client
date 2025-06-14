import datetime
import http.client as http_client
import json
import os
import time

import daaily.credentials
import daaily.exceptions
import daaily.transport.exceptions

DAAILY_USER_EMAIL_ENV = "DAAILY_USER_EMAIL"
DAAILY_USER_UID_ENV = "DAAILY_USER_UID"
DAAILY_USER_API_KEY_ENV = "DAAILY_USER_API_KEY"
MISSING_ENV_USER_CREDENTIALS_MESSAGE = (
    "You either have to pass the user credentials are set them via the environment."
)
SALLY_BASE_URL = "https://sally.daaily.com/api/v3"
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
                user_email = os.environ[DAAILY_USER_EMAIL_ENV]
                user_uid = os.environ[DAAILY_USER_UID_ENV]
                api_key = os.environ[DAAILY_USER_API_KEY_ENV]
            except KeyError as e:
                raise daaily.exceptions.MissingEnvironmentVariable(
                    f"{MISSING_ENV_USER_CREDENTIALS_MESSAGE}\nError: {str(e.args)}"
                ) from e
        self._user_email = user_email
        self._user_uid = user_uid
        self._api_key = api_key
        self._get_token_endpoint = f"{SALLY_BASE_URL}/{TOKEN_ENDPOINT}"
        self._get_token_with_refresh_token_endpoint = (
            f"{SALLY_BASE_URL}/{REFRESH_ENDPOINT}"
        )
        self._api_key_header = {"Authorization": f"ApiKey {self._api_key}"}

    def _make_request(
        self,
        request,
        url: str,
        headers: dict | None = None,
        request_body: dict | None = None,
    ):
        max_retries = 10
        retry_delay = 1
        attempt = 0
        while attempt < max_retries:
            body = request_body
            if request_body is not None:
                body = json.dumps(request_body)
            response = request(
                url=url,
                method="POST",
                headers=headers,
                body=body,
            )
            if response.status == http_client.OK:
                response_body = (
                    response.data.decode("utf-8")
                    if hasattr(response.data, "decode")
                    else response.data
                )
                response_data = json.loads(response_body)
                return response_data
            elif response.status == 429:  # Too Many Requests
                attempt += 1
                retry_after = response.headers.get("Retry-After")
                if retry_after:
                    retry_delay = int(retry_after)
                else:
                    retry_delay *= 2
                time.sleep(retry_delay)
            else:
                raise daaily.transport.exceptions.TransportException(
                    response, response.data
                )
        raise daaily.transport.exceptions.TransportException(response, response.data)

    def refresh(self, request):
        if self.id_token and self.refresh_token:
            response_data = self.get_token_with_refresh_token(
                request, self.refresh_token
            )
        else:
            response_data = self.get_token(request)
        now = datetime.datetime.utcnow()
        self.id_token = response_data.get("id_token")
        if "refresh_token" in response_data:
            self.refresh_token = response_data["refresh_token"]
        lifetime = datetime.timedelta(seconds=int(response_data.get("expires_in")))
        self.expiry = now + lifetime

    def get_token(self, request):
        """Exchanges a refresh token for an access token based on the
        RFC6749 spec.

        Args:
            request (google.auth.transport.Request): A callable used to make
                HTTP requests.
            subject_token (str): The OAuth 2.0 refresh token.
        """
        return self._make_request(
            request=request,
            url=self._get_token_endpoint,
            headers=self._api_key_header,
            request_body={"email": f"{self._user_email}", "uid": f"{self._user_uid}"},
        )

    def get_token_with_refresh_token(self, request, refresh_token: str):
        """Exchanges a refresh token for an access token based on the
        RFC6749 spec.

        Args:
            request (google.auth.transport.Request): A callable used to make
                HTTP requests.
            subject_token (str): The OAuth 2.0 refresh token.
        """
        return self._make_request(
            request=request,
            url=self._get_token_with_refresh_token_endpoint,
            headers=self._api_key_header,
            request_body={
                "email": f"{self._user_email}",
                "refresh_token": refresh_token,
            },
        )
