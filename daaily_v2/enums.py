from enum import Enum


class Environment(Enum):
    PRODUCTION = "production"
    STAGING = "staging"


class HttpResponseCode(Enum):
    HTTP_200_OK = 200
    HTTP_401_UNAUTHORIZED = 401
    HTTP_403_FORBIDDEN = 403
