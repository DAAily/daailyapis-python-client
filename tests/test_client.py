import os

import pytest
import urllib3

import daaily.credentials_sally as creds_sally
import daaily.exceptions
import daaily.transport.urllib3_http


class TestAuthSallyCredentials:
    def test_client_init(self):
        credentials = creds_sally.Credentials(
            user_email="justus.voigt@daaily.com", user_uid="1234", api_key="1234"
        )
        assert credentials.id_token is None

    def test_client_init_with_env_values(self):
        os.environ[creds_sally.DAAILY_USER_EMAIL_ENV] = "justus.voigt@daaily.com"
        os.environ[creds_sally.DAAILY_USER_UID_ENV] = "1234"
        os.environ[creds_sally.DAAILY_API_KEY_ENV] = "1234"
        credentials = creds_sally.Credentials()
        assert credentials._api_key == "1234"
        assert credentials._user_uid == "1234"
        assert credentials._user_email == "justus.voigt@daaily.com"
        os.environ.pop(creds_sally.DAAILY_USER_EMAIL_ENV)
        os.environ.pop(creds_sally.DAAILY_USER_UID_ENV)
        os.environ.pop(creds_sally.DAAILY_API_KEY_ENV)

    def test_client_init_without_env_values(self):
        # this test is following the order of execution within the init func
        with pytest.raises(daaily.exceptions.MissingEnvironmentVariable) as e:
            creds_sally.Credentials()
        assert creds_sally.DAAILY_USER_EMAIL_ENV in str(e.value)
        os.environ[creds_sally.DAAILY_USER_EMAIL_ENV] = "justus.voigt@daaily.com"
        with pytest.raises(daaily.exceptions.MissingEnvironmentVariable) as e:
            creds_sally.Credentials()
        assert creds_sally.DAAILY_USER_UID_ENV in str(e.value)
        os.environ[creds_sally.DAAILY_USER_UID_ENV] = "1234"
        with pytest.raises(daaily.exceptions.MissingEnvironmentVariable) as e:
            creds_sally.Credentials()
        assert creds_sally.DAAILY_API_KEY_ENV in str(e.value)
        os.environ.pop(creds_sally.DAAILY_USER_EMAIL_ENV)
        os.environ.pop(creds_sally.DAAILY_USER_UID_ENV)

    @pytest.mark.skip("Misses the stub for the http request")
    def test_make_auth_request_to_sally(self):
        http = urllib3.PoolManager()
        request = daaily.transport.urllib3_http.Request(http)
        credentials = creds_sally.Credentials(
            user_email="justus.voigt@daaily.com",
            user_uid="",
            api_key="",
        )
        credentials.refresh(request)
