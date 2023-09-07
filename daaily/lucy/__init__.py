import abc

# import daaily.lucy.enums


class Client(metaclass=abc.ABCMeta):
    """
    Interface that makes requests to Lucy.
    """

    @abc.abstractmethod
    def get_entities(
        self,
        type: str,
        filter=None,
        disable_pagination=False,
        limit=500,
        **kwargs,
    ):
        """Make an HTTP request.

        Args:
            type (Enum): The type to be requested.
            filter (ANY): Filter to be applied to the request.
            disable_pagination (bool): Speed up request time by disabling pagination.
            limit (int): Limit the number of entities returned. This works
                independently of pagination.
            kwargs: Additionally arguments passed on to the Lucy client's.

        Returns:
            Response: The HTTP response.

        Raises:
            daaily.transport.exceptions.TransportException: If any exception occurred.
        """
        raise NotImplementedError("get_entities must be implemented.")
