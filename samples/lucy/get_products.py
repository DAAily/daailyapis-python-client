from dotenv import load_dotenv

from daaily.credentials_sally import Credentials
from daaily.lucy.constants import LUCY_V2_BASE_URL_STAGING
from daaily.transport.urllib3_http import AuthorizedHttp


def main():
    load_dotenv()
    creds = Credentials()
    s = AuthorizedHttp(creds)

    r = s.request("GET", f"{LUCY_V2_BASE_URL_STAGING}/products")
    print(r.data)
