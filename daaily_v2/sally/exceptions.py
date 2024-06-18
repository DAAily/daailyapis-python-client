class MissingEnvironmentVariable(Exception):
    """Required environment variables are missing."""

    pass


class MissingRefreshToken(Exception):
    """Required refresh token is missing."""

    pass


class SallyRequestFailed(Exception):
    """Request to Sally are failing."""

    pass
