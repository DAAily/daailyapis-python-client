import json
import os

from urllib3 import BaseHTTPResponse

from daaily_v2.sally.constants import (
    DAAILY_USER_API_KEY_ENV,
    DAAILY_USER_EMAIL_ENV,
    DAAILY_USER_UID_ENV,
    MISSING_ENV_USER_CREDENTIALS_MESSAGE,
    REFRESH_ENDPOINT,
    SALLY_BASE_URL,
    TOKEN_ENDPOINT,
)
from daaily_v2.sally.exceptions import MissingEnvironmentVariable


def load_auth_env_values() -> tuple[str, str, str]:
    try:
        user_email = os.environ[DAAILY_USER_EMAIL_ENV]
        user_uid = os.environ[DAAILY_USER_UID_ENV]
        api_key = os.environ[DAAILY_USER_API_KEY_ENV]
    except KeyError as error:
        raise MissingEnvironmentVariable(
            f"{MISSING_ENV_USER_CREDENTIALS_MESSAGE}\nError: {str(error.args)}"
        ) from error
    return user_email, user_uid, api_key


def gen_refresh_token_url(api_key: str) -> str:
    refersh_token_url = f"{SALLY_BASE_URL}/{REFRESH_ENDPOINT}?key={api_key}"
    return refersh_token_url


def gen_refresh_token_body(user_email: str, refresh_token: str) -> dict:
    request_body = {"email": f"{user_email}", "refresh_token": refresh_token}
    return request_body


def gen_get_token_url(api_key: str) -> str:
    get_token_url = f"{SALLY_BASE_URL}/{TOKEN_ENDPOINT}?key={api_key}"
    return get_token_url


def gen_get_token_body(user_email: str, user_uid: str) -> dict:
    request_body = {"email": f"{user_email}", "uid": user_uid}
    return request_body


def extract_token_detail(http_response: BaseHTTPResponse) -> tuple[str, str, int]:
    response_body = (
        http_response.data.decode("utf-8")
        if hasattr(http_response.data, "decode")
        else http_response.data
    )
    response_data: dict = json.loads(response_body)
    id_token = response_data.get("id_token", "")
    refresh_token = response_data.get("refresh_token", "")
    expires_in = response_data.get("expires_in", "")
    return id_token, refresh_token, int(expires_in)
