from datetime import datetime, timedelta

import httpx

from daaily.http.client import Client as HttpClient
from daaily.sally.constants import (
    MISSING_REFRESH_TOKEN_MESSAGE,
    REFRESH_THRESHOLD_SECS,
)
from daaily.sally.exceptions import MissingRefreshToken
from daaily.sally.utility import (
    extract_token_detail,
    gen_get_token_body,
    gen_get_token_url,
    gen_refresh_token_body,
    gen_refresh_token_url,
    load_auth_env_values,
)


class Client:
    def __init__(self) -> None:
        # ENV USER CREDENTIALS
        user_email, user_uid, api_key = load_auth_env_values()
        self._user_email = user_email
        self._user_uid = user_uid
        self._api_key = api_key
        # TOKEN DETAIL
        self.refresh_token: str | None = None
        self.expiry: datetime | None = None
        self.id_token: str | None = None
        # HTTP REQUESTS
        self.http_client = HttpClient()

    def _is_expired(self) -> bool:
        if not self.expiry:
            return False
        refresh_buffer = timedelta(seconds=REFRESH_THRESHOLD_SECS)
        skewed_expiry = self.expiry - refresh_buffer
        return datetime.now() >= skewed_expiry

    def _set_expiry(self, expires_in: int) -> None:
        limeftime = timedelta(seconds=expires_in)
        self.expiry = datetime.now() + limeftime

    def _set_token_detail(self, response: httpx.Response) -> None:
        id_token, refresh_token, expires_in = extract_token_detail(response)
        self.id_token = id_token
        self.refresh_token = refresh_token
        self._set_expiry(expires_in)

    async def _refresh_token(self) -> None:
        if not self.refresh_token:
            raise MissingRefreshToken(MISSING_REFRESH_TOKEN_MESSAGE)
        refresh_token_url = gen_refresh_token_url(self._api_key)
        request_body = gen_refresh_token_body(self._user_email, self.refresh_token)
        response = await self.http_client.post_request(
            refresh_token_url, request_body, None
        )
        self._set_token_detail(response)

    async def get_token(self) -> str:
        if self.id_token:
            if self._is_expired():
                await self._refresh_token()
            return self.id_token
        get_token_url = gen_get_token_url(self._api_key)
        request_body = gen_get_token_body(self._user_email, self._user_uid)
        response = await self.http_client.post_request(
            get_token_url, request_body, None
        )
        self._set_token_detail(response)
        return self.id_token  # type: ignore
