from dotenv import load_dotenv

from daaily.credentials_sally import Credentials
from daaily.transport.urllib3_http import AuthorizedHttp

load_dotenv()

creds = Credentials()
s = AuthorizedHttp(creds)

def main():
    pass
    r = s.request("GET", "https://lucy.daaily.com/api/v2/products")
    print(r.data)
