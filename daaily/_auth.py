# from .models import Credentials
import datetime
import os

from . import _utils as utils
from .exceptions import MissingEnvironmentVariable

REFRESH_THRESHOLD_SECS = 600
DAAILY_USER_EMAIL_ENV = "DAAILY_USER_EMAIL"
DAAILY_USER_UID_ENV = "DAAILY_USER_UID"
DAAILY_API_KEY_ENV = "DAAILY_API_KEY"
MISSING_ENV_USER_CREDENTIALS_MESSAGE = (
    "You either have to pass the user credentials are set them via the environment."
)


class Credentials:
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
        # self.credentials = credentials
        self._id_token = None
        self._refresh_token = None
        self._expiry = None
        # self._user_email = user_email
        # self._user_uid = user_uid
        # self._api_key = api_key

        if user_email is None or user_uid is None or api_key is None:
            try:
                user_email = os.environ["DAAILY_USER_EMAIL"]
                user_uid = os.environ["DAAILY_USER_UID"]
                api_key = os.environ["DAAILY_API_KEY"]
            except KeyError as e:
                raise MissingEnvironmentVariable(
                    f"{MISSING_ENV_USER_CREDENTIALS_MESSAGE}\nError: {str(e.args)}"
                ) from e

        self._user_email = user_email
        self._user_uid = user_uid
        self._api_key = api_key

    def _get_values_from_environment(self):
        """
        Gets the values from the environment.
        """
        pass

    def _refresh(self):
        """
        Refreshes the credentials for the client.
        """
        print("this is the refresh method")
        pass

    # @utils.refresh_decorator
    @property
    def id_token(self) -> str | None:
        """
        Returns the id token used to authenticate with a client.
        """
        return self._id_token

    @property
    def expired(self) -> bool:
        """Checks if the credentials are expired.

        Note that credentials can be invalid but not expired because
        Credentials with :attr:`expiry` set to None is considered to never
        expire.
        """
        if not self._expiry:
            return False
        skewed_expiry = self._expiry - REFRESH_THRESHOLD_SECS
        return datetime.datetime.utcnow() >= skewed_expiry
        # return _helpers.utcnow() >= skewed_expiry

    @property
    def valid(self):
        """Checks the validity of the credentials.

        This is True if the credentials have a :attr:`token` and the token
        is not :attr:`expired`.
        """
        return self._id_token is not None and not self.expired

    def _update_credentials(self, out):
        """
        Updates the credentials for the client.
        """
        pass

    def apply_to_header(self, headers, id_token=None):
        """Apply the token to the authentication header.

        Args:
            headers (Mapping): The HTTP request headers.
            id_token (Optional[str]): If specified, overrides the current id token.
        """
        headers["authorization"] = f"Bearer {id_token or self._id_token}"

    def refresh(self, request):
        pass

    def before_request(self, request, method, url, headers):
        """Performs credential-specific before request logic.

        Refreshes the credentials if necessary, then calls :meth:`apply` to
        apply the token to the authentication header.

        Args:
            request (google.auth.transport.Request): The object used to make
                HTTP requests.
            method (str): The request's HTTP method or the RPC method being
                invoked.
            url (str): The request's URI or the RPC service's URI.
            headers (Mapping): The request's headers.
        """
        # pylint: disable=unused-argument
        # (Subclasses may use these arguments to ascertain information about
        # the http request.)
        if not self.valid:
            self.refresh(request)
        # metrics.add_metric_header(headers, self._metric_header_for_usage())
        self.apply_to_header(headers)

    # @utils.refresh_decorator
    # def get_id_token(self) -> str | None:
    #     """
    #     Returns the id token used to authenticate with a client.
    #     """
    #     return self._id_token
