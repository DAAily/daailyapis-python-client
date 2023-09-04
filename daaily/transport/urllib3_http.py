# from urllib3 import PoolManager
import urllib3
from urllib3.request import RequestMethods

# import daaily.transport
import daaily.transport
from daaily.credentials import Credentials


class _Response(daaily.transport.Response):
    """urllib3 transport response adapter.

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

    def __init__(self, http=None):
        if http is None:
            http = urllib3.PoolManager()
        self.http = http

    def __call__(
        self, url, method="GET", body=None, headers=None, timeout=None, **kwargs
    ):
        """Make an HTTP request using urllib3.

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
            google.auth.transport.Response: The HTTP response.

        Raises:
            google.auth.exceptions.TransportError: If any exception occurred.
        """
        if timeout is not None:
            kwargs["timeout"] = timeout
        response = self.http.request(method, url, body=body, headers=headers, **kwargs)
        return _Response(response)

    # def get_request(self, url, **kwargs):
    #     raise NotImplementedError("Custom request handlers are not supported yet.")
    #     # return self.request("GET", url, **kwargs)


class AuthorizedHttp(RequestMethods):
    """A urllib3 HTTP class with credentials.

    This class is used to perform requests to API endpoints that require
    authorization::

        from google.auth.transport.urllib3 import AuthorizedHttp

        auth_http = AuthorizedHttp(credentials)

        response = auth_http.request(
            'GET', 'https://www.googleapis.com/storage/v1/b')

    This class implements :class:`urllib3.request.RequestMethods` and can be
    used just like any other :class:`urllib3.PoolManager`.

    The underlying :meth:`urlopen` implementation handles adding the
    credentials' headers to the request and refreshing credentials as needed.

    Args:
        credentials (google.auth.credentials.Credentials): The credentials to
            add to the request.
        http (urllib3.PoolManager): The underlying HTTP object to
            use to make requests. If not specified, a
            :class:`urllib3.PoolManager` instance will be constructed with
            sane defaults.
    """

    def __init__(
        self,
        credentials: Credentials,
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


# class AuthorizedRequest(RequestMethods):
#     def __init__(self, credentials):
#         self._credentials = credentials

# def _before_requVjjjjjjjjjest(self, credentials: Credentials, headers):
#     """Performs credential-specific before request logic.

#     Refreshes the credentials if necessary, then calls :meth:`apply` to
#     apply the token to the authentication header.

#     Args:
#         request (google.auth.transport.Request): The object used to make
#             HTTP requests.
#         method (str): The request's HTTP method or the RPC method being
#             invoked.
#         url (str): The request's URI or the RPC service's URI.
#         headers (Mapping): The request's headers.
#     """
#     # pylint: disable=unused-argument
#     # (Subclasses may use these arguments to ascertain information about
#     # the http request.)
#     if not credentials.valid:
#         credentials.refresh()
#     # metrics.add_metric_header(headers, self._metric_header_for_usage())
#     credentials.apply_to_header(headers)

# def execute(self) -> http_client.HTTPResponse:
#     """
#     Executes the request.
#     """

#     self._before_request(selapply_headers)
#     with self.urlopen(self.method, self.url, self.body, self.headers) as resp:
#         return resp

# def _retry_request(
#     self, num_retries, uri, method="GET", body=None, headers=None
# ) -> tuple:
#     """Request with exponential backoff.

#     Args:
#       http: httplib2.Http, an http object to be used in place of the
#             one the HttpRequest request object was constructed with.
#       num_retries: Integer, number of times to retry with randomized
#             exponential backoff. If all retries fail, the raised HttpError
#             represents the last request. If zero (default), we attempt the
#             request only once.
#       sleep: callable, a function that takes one argument, a number of
#             seconds, and sleeps for that long before returning.
#       rand: callable, a function that takes no arguments and returns a
#             random float between 0 and 1.
#       uri: string, the URI to be requested, relative to the API root URL.
#       method: string, the HTTP method to use for the request.
#       body: string, the body of the HTTP request.
#       headers: dict, the HTTP headers to send with the request.

#     Returns:
#       A tuple of (httplib2.Response, string), where the first value is the
#       HTTP response object and the second value is the string response from
#       the server.

#     Raises:
#       googleapiclient.errors.HttpError if the response was not a 2xx.
#       httplib2.HttpLib2Error if a transport error has occurred.
#     """
#     if num_retries < 0:
#         raise ValueError("num_retries must be >= 0")

#     if num_retries == 0:
#         resp, content = self.request(
#             url=uri, method=method, body=body, headers=headers
#         )
#     else:
#         for n in range(num_retries + 1):
#             resp, content = self.request(
#                 url=uri, method=method, body=body, headers=headers
#             )
#             if resp.status < 500:
#                 break
#             if n == num_retries:
#                 break
#             # sleep(_rand_between(rand, 0, 2**n - 1))
#     return resp, content

# def __init__(self, credentials: Credentials | None = None):
#     """
#     Creates a new Lucy client.
#     """
#     if credentials is None:
#         credentials = Credentials()
# self.credentials = credentials
# pass
# return self._retry_request(
#     num_retries, self.uri, self.method, self.body, self.headers
# )

# @authenticated_request
