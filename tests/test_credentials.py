import datetime

import daaily.credentials
import daaily.credentials_sally


class CredentialsImpl(daaily.credentials.Credentials):
    def refresh(self, request):
        self.id_token = request


def test_credentials_constructor():
    credentials = CredentialsImpl()
    assert not credentials.id_token
    assert not credentials.expiry
    assert not credentials.expired
    assert not credentials.valid


def test_expired_and_valid():
    credentials = CredentialsImpl()
    credentials.id_token = "token"
    assert credentials.valid
    assert not credentials.expired
    # Set the expiration to one second more than now plus the clock skew
    # accommodation. These credentials should be valid.
    credentials.expiry = datetime.datetime.fromtimestamp(
        datetime.datetime.utcnow().timestamp()
        + daaily.credentials.REFRESH_THRESHOLD_SECS
        + datetime.timedelta(seconds=1).seconds
    )
    assert credentials.valid
    assert not credentials.expired
    # Set the credentials expiration to now. Because of the clock skew
    # accommodation, these credentials should report as expired.
    credentials.expiry = datetime.datetime.utcnow()
    assert not credentials.valid
    assert credentials.expired


def test_before_request():
    credentials = CredentialsImpl()
    request = "token"
    headers = {}
    # First call should call refresh, setting the token.
    credentials.before_request(request, headers)
    assert credentials.valid
    assert credentials.id_token == "token"
    assert headers["authorization"] == "Bearer token"
    request = "token2"
    headers = {}
    # Second call shouldn't call refresh.
    credentials.before_request(request, headers)
    assert credentials.valid
    assert credentials.id_token == "token"
    assert headers["authorization"] == "Bearer token"
