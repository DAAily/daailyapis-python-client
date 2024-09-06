import json

import httpx

from daaily.enums import DaailyService
from daaily.http.enums import HttpAuthType, HttpResponseCode
from daaily.http.models import HttpResponse


def add_authorization_header(
    auth_type: HttpAuthType, auth_token: str, headers: dict | None
) -> dict:
    auth_header = {"Authorization": f"{auth_type.value} {auth_token}"}
    if headers is not None:
        headers.update(auth_header)
        return headers
    return auth_header


def extract_response_data(
    response: httpx.Response,
    service_name: DaailyService | None = None,
    check_response_code: bool = True,
):
    service_name_string = service_name.value if service_name else "Daaily Service"
    if check_response_code:
        if response.status_code >= HttpResponseCode.HTTP_400_BAD_REQUEST:
            raise Exception(
                f"Error requesting {service_name_string}: " + str(response.content)
            )
    return HttpResponse(
        data=json.loads(response.content),
        status_code=response.status_code,
        headers=response.headers,
    )
