import pytest

import daaily.transport.urllib3_http
from daaily.credentials_sally import Credentials

MANUFACTURER_ID = 1
MANUFACTURER_NAME = "This never would never exists on Architonic"
URL = "https://lucy.daaily.com/api/v2/manufacturers"

creds = Credentials()
auth_s = daaily.transport.urllib3_http.AuthorizedHttp(creds)


class TestAuthorizedHttpClient:
    @pytest.mark.skip("This is a integrated test and should be run manually only")
    def test_get_manufacturer_by_id(self):
        """Retrieve the manufacturer name from the Lucy API"""
        full_url = f"{URL}/{MANUFACTURER_ID}"
        r = auth_s.request("GET", full_url)
        assert r.status == 404

    @pytest.mark.skip("This is a integrated test and should be run manually only")
    def test_get_manufacturers_by_name_like(self):
        """Retrieve the manufacturer name from the Lucy API"""
        full_url = f"{URL}?manufacturer_name={MANUFACTURER_NAME}"
        r = auth_s.request("GET", full_url)
        assert r.status == 404
