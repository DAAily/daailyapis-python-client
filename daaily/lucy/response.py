import json
from typing import Mapping

import daaily.transport


class Response(daaily.transport.Response):
    def __init__(self, status: int, headers: Mapping[str, str], data: bytes):
        self._status = status
        self._headers = headers
        self._data = data

    @property
    def status(self) -> int:
        """int: The HTTP status code."""
        return self._status

    @property
    def headers(self) -> Mapping[str, str]:
        """Mapping[str, str]: The HTTP response headers."""
        return self._headers

    @property
    def data(self) -> bytes:
        """bytes: The response body."""
        return self._data

    def json(self) -> dict | None:
        """
        Parses the response body as JSON and returns the resulting object.

        This method attempts to decode the response body as a JSON object and
        returns the resulting dictionary. It only performs this operation if
        the HTTP status code is between 200 and 299 (inclusive). If the status
        code is outside this range, the method returns None.

        Returns:
            dict | None: The parsed JSON object if the status code is 200-299,
            otherwise None.

        Raises:
            json.JSONDecodeError: If the response body cannot be decoded as JSON.
        """
        if self._status < 200 or self._status >= 300:
            return None
        return json.loads(self._data.decode("utf-8"))

    @classmethod
    def from_response(cls, response: daaily.transport.Response) -> "Response":
        return cls(
            status=response.status,
            headers=response.headers,
            data=response.data,
        )
