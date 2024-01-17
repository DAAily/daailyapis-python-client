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
    credentials.expiry = datetime.datetime.utcnow() + datetime.timedelta(seconds=3600)
    assert credentials.valid
    assert not credentials.expired
    credentials.expiry = datetime.datetime.utcnow() - datetime.timedelta(seconds=3600)
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
