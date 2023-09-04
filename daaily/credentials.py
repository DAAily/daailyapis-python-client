import abc
import datetime

REFRESH_THRESHOLD_SECS = 600


class Credentials(metaclass=abc.ABCMeta):
    """
    The Lucy client is used to interact with the Lucy server.
    It provides functionality in order to make requests to each of Lucy's endpoints
    including the ability to create, update, and delete objects.
    You will also be able to specify to either use the client in a synchronous or
    asynchronous manner.
    """

    def __init__(self):
        """
        Initializes authentication that is required for Daaily clients.
        """
        self._id_token = None
        self._refresh_token = None
        self._expiry = None

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

    @property
    def valid(self):
        """Checks the validity of the credentials.

        This is True if the credentials have a :attr:`token` and the token
        is not :attr:`expired`.
        """
        return self._id_token is not None and not self.expired

    @abc.abstractmethod
    def refresh(self, request):
        raise NotImplementedError("Refresh must be implemented")

    def apply_to_header(self, headers: dict, id_token=None):
        """Apply the token to the authentication header.

        Args:
            headers (Mapping): The HTTP request headers.
            id_token (Optional[str]): If specified, overrides the current id token.
        """
        headers["authorization"] = f"Bearer {id_token or self._id_token}"

    def before_request(self, request, headers):
        """Performs credential-specific before request logic.

        Refreshes the credentials if necessary, then calls :meth:`apply_to_header` to
        apply the token to the authentication header.
        """
        if not self.valid:
            self.refresh(request)
        self.apply_to_header(headers)
