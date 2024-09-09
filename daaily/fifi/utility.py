import os

from daaily.enums import Environment
from daaily.exceptions import MissingEnvironmentVariable
from daaily.fifi.constants import (
    FIFI_AUTH_PASSWORD_ENV,
    FIFI_AUTH_USERNAME_ENV,
    MISSING_ENV_FIFI_CREDENTIALS_MESSAGE,
)
from daaily.fifi.enums import FifiEndpoint, FifiProcessType


def gen_fifi_endpoint_url(
    environment: Environment, process_type: FifiProcessType, endpoint: FifiEndpoint
) -> str:
    if environment == Environment.PRODUCTION:
        return f"https://fifi.daaily.com/api/{process_type.value}{endpoint.value}"
    return f"https://fifi.staging.daaily.com/api/{process_type.value}{endpoint.value}"


def load_auth_env_values() -> tuple[str, str]:
    try:
        username = os.environ[FIFI_AUTH_USERNAME_ENV]
        password = os.environ[FIFI_AUTH_PASSWORD_ENV]
    except KeyError as error:
        raise MissingEnvironmentVariable(
            f"{MISSING_ENV_FIFI_CREDENTIALS_MESSAGE}\nError: {str(error.args)}"
        ) from error
    return username, password
