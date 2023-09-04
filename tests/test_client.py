from daaily.auth_sally import Credentials


class TestClient:
    def test_client_init(self):
        credentials = Credentials(
            user_email="justus.voigt@daaily.com", user_uid="1234", api_key="1234"
        )
        assert credentials.id_token is None
