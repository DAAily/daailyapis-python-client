from enum import Enum


class HttpResponseCode(int, Enum):
    HTTP_200_OK = 200
    HTTP_400_BAD_REQUEST = 400
    HTTP_401_UNAUTHORIZED = 401
    HTTP_403_FORBIDDEN = 403


class HttpAuthType(str, Enum):
    BASIC = "Basic"
    BEARER = "Bearer"
