import urllib3
from urllib3.request import RequestMethods

import daaily.credentials
import daaily.transport


class _Response(daaily.transport.Response):
    """
    urllib3 transport response adapter.

    Args:
        response (urllib3.response.HTTPResponse): The raw urllib3 response.
    """

    def __init__(self, response):
        self._response = response

    @property
    def status(self):
        return self._response.status

    @property
    def headers(self):
        return self._response.headers

    @property
    def data(self):
        return self._response.data


class Request(daaily.transport.Request):
    """
    The Lucy client is used to interact with the Lucy server.
    It provides functionality in order to make requests to each of Lucy's endpoints
    including the ability to create, update, and delete objects.
    You will also be able to specify to either use the client in a synchronous or
    asynchronous manner.
    """

    def __init__(self, http):
        self.http = http

    def __call__(
        self, url, method="GET", body=None, headers=None, timeout=None, **kwargs
    ):
        """
        Make an HTTP request using urllib3.

        Args:
            url (str): The URI to be requested.
            method (str): The HTTP method to use for the request. Defaults
                to 'GET'.
            body (bytes): The payload / body in HTTP request.
            headers (Mapping[str, str]): Request headers.
            timeout (Optional[int]): The number of seconds to wait for a
                response from the server. If not specified or if None, the
                urllib3 default timeout will be used.
            kwargs: Additional arguments passed through to the underlying
                urllib3 :meth:`urlopen` method.

        Returns:
            daaily.transport.Response: The HTTP response.

        Raises:
            daaily.transport.exceptions.TransportException: If any exception occurred.
        """
        if timeout is not None:
            kwargs["timeout"] = timeout
        response = self.http.request(method, url, body=body, headers=headers, **kwargs)
        return _Response(response)


class AuthorizedHttp(RequestMethods):
    """
    A urllib3 HTTP class with credentials.

    This class is used to perform requests to API endpoints that require
    authorization::

        from daaily.transport.urllib3_http import AuthorizedHttp

        auth_http = AuthorizedHttp(credentials)

        response = auth_http.request(
            'GET', 'https://www.lucy.daaily.com/api/v2/products')

    This class implements :class:`urllib3.request.RequestMethods` and can be
    used just like any other :class:`urllib3.PoolManager`.

    The underlying :meth:`urlopen` implementation handles adding the
    credentials' headers to the request and refreshing credentials as needed.

    Args:
        credentials (daaily.credentials.Credentials): The credentials to
            add to the request.
        http (urllib3.PoolManager): The underlying HTTP object to
            use to make requests. If not specified, a
            :class:`urllib3.PoolManager` instance will be constructed with
            sane defaults.
    """

    def __init__(
        self,
        credentials: daaily.Credentials,
        http=None,
        refresh_status_codes=daaily.transport.DEFAULT_REFRESH_STATUS_CODES,
        max_refresh_attempts=daaily.transport.DEFAULT_MAX_REFRESH_ATTEMPTS,
    ):
        if http is None:
            http = urllib3.PoolManager()
        self.http = http
        self.credentials = credentials
        self._refresh_status_codes = refresh_status_codes
        self._max_refresh_attempts = max_refresh_attempts
        self._request = Request(self.http)
        super(AuthorizedHttp, self).__init__()

    def urlopen(self, method, url, body=None, headers=None, **kwargs):
        """Implementation of urllib3's urlopen."""
        # We use kwargs to collect additional args that we don't need to
        # introspect here. However, we do explicitly collect the two
        # positional arguments.
        _refresh_attempt = kwargs.pop("_refresh_attempt", 0)
        if headers is None:
            headers = self.headers
        # Make a copy of the headers. They will be modified by the credentials
        # and we want to pass the original headers if we recurse.
        request_headers = headers.copy()
        self.credentials.before_request(self._request, request_headers)
        response = self.http.urlopen(
            method, url, body=body, headers=request_headers, **kwargs
        )
        # If the response indicated that the credentials needed to be
        # refreshed, then refresh the credentials and re-attempt the
        # request.
        # A stored token may expire between the time it is retrieved and
        # the time the request is made, so we may need to try twice.
        # The reason urllib3's retries aren't used is because they
        # don't allow you to modify the request headers. :/
        if (
            response.status in self._refresh_status_codes
            and _refresh_attempt < self._max_refresh_attempts
        ):
            self.credentials.refresh(self._request)
            return self.urlopen(
                method,
                url,
                body=body,
                headers=headers,
                _refresh_attempt=_refresh_attempt + 1,
                **kwargs,
            )
        return response

    # Proxy methods for compliance with the urllib3.PoolManager interface

    def __enter__(self):
        """Proxy to ``self.http``."""
        return self.http.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Proxy to ``self.http``."""
        return self.http.__exit__(exc_type, exc_val, exc_tb)

    def __del__(self):
        if hasattr(self, "http") and self.http is not None:
            self.http.clear()

    @property
    def headers(self):
        """Proxy to ``self.http``."""
        return self.http.headers

    @headers.setter
    def headers(self, value):
        """Proxy to ``self.http``."""
        self.http.headers = value
