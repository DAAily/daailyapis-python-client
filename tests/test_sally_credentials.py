import datetime
import os
from unittest.mock import patch

import pytest
import urllib3

import daaily.credentials_sally
import daaily.exceptions
import daaily.transport.urllib3_http


class CredentialsStub(daaily.credentials_sally.Credentials):
    def __init__(self, id_token=None):
        self.id_token = id_token
        self._user_email = "justus@nice.com"
        self._user_uid = "some-user-uid"
        self._api_key = "some-api-key"

    # def apply(self, headers, id_token=None):
    #     headers["authorization"] = self.id_token

    # def before_request(self, request, headers):
    #     self.apply(headers)


class TestAuthSallyCredentials:
    now = datetime.datetime.utcnow()

    def test_refresh(self):
        credentials = CredentialsStub()
        http = urllib3.PoolManager()
        request = daaily.transport.urllib3_http.Request(http)
        return_value = {
            "access_token": "ey-access-token",
            "expires_in": "3600",
            "token_type": "Bearer",
            "refresh_token": "AMf-refresh-token",
            "id_token": "ey-id-token",
            "user_id": "some-user-uid",
            "project_id": "project-id",
        }
        with patch(
            target="tests.utils.datetime.datetime.utcnow",
            return_value=TestAuthSallyCredentials.now,
        ):
            with patch(
                "daaily.credentials_sally.Credentials.get_token",
                return_value=return_value,
            ):
                credentials.refresh(request)
        assert credentials.id_token == "ey-id-token"
        assert credentials.refresh_token == "AMf-refresh-token"
        assert credentials.expiry == TestAuthSallyCredentials.now + datetime.timedelta(
            seconds=3600
        )

    def test_client_init(self):
        credentials = daaily.credentials_sally.Credentials(
            user_email="justus.voigt@daaily.com", user_uid="1234", api_key="1234"
        )
        assert credentials.id_token is None

    def test_client_init_with_env_values(self):
        os.environ[
            daaily.credentials_sally.DAAILY_USER_EMAIL_ENV
        ] = "justus.voigt@daaily.com"
        os.environ[daaily.credentials_sally.DAAILY_USER_UID_ENV] = "1234"
        os.environ[daaily.credentials_sally.DAAILY_USER_API_KEY_ENV] = "1234"
        credentials = daaily.credentials_sally.Credentials()
        assert credentials._api_key == "1234"
        assert credentials._user_uid == "1234"
        assert credentials._user_email == "justus.voigt@daaily.com"
        os.environ.pop(daaily.credentials_sally.DAAILY_USER_EMAIL_ENV)
        os.environ.pop(daaily.credentials_sally.DAAILY_USER_UID_ENV)
        os.environ.pop(daaily.credentials_sally.DAAILY_USER_API_KEY_ENV)

    def test_client_init_without_env_values(self):
        # this test is following the order of execution within the init func
        with pytest.raises(daaily.exceptions.MissingEnvironmentVariable) as e:
            daaily.credentials_sally.Credentials()
        assert daaily.credentials_sally.DAAILY_USER_EMAIL_ENV in str(e.value)
        os.environ[
            daaily.credentials_sally.DAAILY_USER_EMAIL_ENV
        ] = "justus.voigt@daaily.com"
        with pytest.raises(daaily.exceptions.MissingEnvironmentVariable) as e:
            daaily.credentials_sally.Credentials()
        assert daaily.credentials_sally.DAAILY_USER_UID_ENV in str(e.value)
        os.environ[daaily.credentials_sally.DAAILY_USER_UID_ENV] = "1234"
        with pytest.raises(daaily.exceptions.MissingEnvironmentVariable) as e:
            daaily.credentials_sally.Credentials()
        assert daaily.credentials_sally.DAAILY_USER_API_KEY_ENV in str(e.value)
        os.environ.pop(daaily.credentials_sally.DAAILY_USER_EMAIL_ENV)
        os.environ.pop(daaily.credentials_sally.DAAILY_USER_UID_ENV)

    @pytest.mark.skip("Misses the stub for the http request")
    def test_make_auth_request_to_sally(self):
        http = urllib3.PoolManager()
        request = daaily.transport.urllib3_http.Request(http)
        credentials = daaily.credentials_sally.Credentials(
            user_email="justus.voigt@daaily.com",
            user_uid="",
            api_key="",
        )
        credentials.refresh(request)
