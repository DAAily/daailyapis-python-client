"""
Transport - HTTP client library support.

:mod:`daaily` is designed to work with various HTTP client libraries such
as urllib3 and requests. In order to work across these libraries with different
interfaces some abstraction is needed.

This module provides two interfaces that are implemented by transport adapters
to support HTTP libraries. :class:`Request` defines the interface expected by
:mod:`daaily` to make requests. :class:`Response` defines the interface
for the return value of :class:`Request`.
"""

import abc
import http.client as http_client

DEFAULT_RETRYABLE_STATUS_CODES = (
    http_client.INTERNAL_SERVER_ERROR,
    http_client.SERVICE_UNAVAILABLE,
    http_client.REQUEST_TIMEOUT,
    http_client.TOO_MANY_REQUESTS,
)
"""Sequence[int]:  HTTP status codes indicating a request can be retried.
"""


DEFAULT_REFRESH_STATUS_CODES = (http_client.UNAUTHORIZED,)
"""Sequence[int]:  Which HTTP status code indicate that credentials should be
refreshed.
"""

DEFAULT_MAX_REFRESH_ATTEMPTS = 2
"""int: How many times to refresh the credentials and retry a request."""


class Response(metaclass=abc.ABCMeta):
    """HTTP Response data."""

    @abc.abstractproperty
    def status(self):
        """int: The HTTP status code."""
        raise NotImplementedError("status must be implemented.")

    @abc.abstractproperty
    def headers(self):
        """Mapping[str, str]: The HTTP response headers."""
        raise NotImplementedError("headers must be implemented.")

    @abc.abstractproperty
    def data(self):
        """bytes: The response body."""
        raise NotImplementedError("data must be implemented.")


class Request(metaclass=abc.ABCMeta):
    """Interface for a callable that makes HTTP requests.

    Specific transport implementations should provide an implementation of
    this that adapts their specific request / response API.

    .. automethod:: __call__
    """

    @abc.abstractmethod
    def __call__(
        self, url, method="GET", body=None, headers=None, timeout=None, **kwargs
    ):
        """Make an HTTP request.

        Args:
            url (str): The URI to be requested.
            method (str): The HTTP method to use for the request. Defaults
                to 'GET'.
            body (bytes): The payload / body in HTTP request.
            headers (Mapping[str, str]): Request headers.
            timeout (Optional[int]): The number of seconds to wait for a
                response from the server. If not specified or if None, the
                transport-specific default timeout will be used.
            kwargs: Additionally arguments passed on to the transport's
                request method.

        Returns:
            Response: The HTTP response.

        Raises:
            daaily.transport.exceptions.TransportException: If any exception occurred.
        """
        raise NotImplementedError("__call__ must be implemented.")
