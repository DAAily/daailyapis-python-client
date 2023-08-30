import unittest
from daaily._auth import Credentials

# from daaily_api.auth import Credentials

# from daaily.models import Credentials


class TestClient(unittest.TestCase):
    def test_client_init(self):
        credentials = Credentials(
            user_email="justus.voigt@daaily.com", user_uid="1234", api_key="1234"
        )
        print(credentials.id_token)
        self.assertTrue(credentials.id_token is not None)
        # client = Client()


if __name__ == "__main__":
    unittest.main()

# unittest.main()
