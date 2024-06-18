import json
from urllib import parse

from urllib3 import BaseHTTPResponse

from daaily_v2.enums import Environment, HttpResponseCode
from daaily_v2.lucy.enums import LucyEndpoint


def get_lucy_v2_endpoint_url(environment: Environment, endpoint: LucyEndpoint) -> str:
    if environment == Environment.PRODUCTION:
        return f"https://lucy.daaily.com/api/v2{endpoint.value}"
    return f"https://lucy.staging.daaily.com/api/v2{endpoint.value}"


def extract_response_data(response: BaseHTTPResponse):
    if response.status != HttpResponseCode.HTTP_200_OK.value:
        raise Exception("Error requesting Lucy: " + str(response.data))
    return json.loads(response.data)


def gen_request_url_with_id(endpoint_url: str, entity_id: int) -> str:
    return f"{endpoint_url}/{entity_id}"


def remove_none_value_params(params: dict) -> None:
    keys_to_delete = []
    for key, value in params.items():
        if value is None:
            keys_to_delete.append(key)
    for key in keys_to_delete:
        del params[key]


def gen_request_url_with_params(endpoint_url: str, params: dict) -> str:
    remove_none_value_params(params)
    query_string = parse.urlencode(params)
    url_with_query = f"{endpoint_url}?{query_string}"
    return url_with_query


def get_manufacturer_params(
    skip: int,
    limit: int,
    manufacturer_ids: list[int] | None = None,
    manufacturer_name: str | None = None,
) -> dict:
    return {
        "skip": skip,
        "limit": limit,
        "manufacturer_ids": ",".join(map(str, manufacturer_ids))
        if manufacturer_ids
        else None,
        "manufacturer_name": manufacturer_name,
    }


def get_distributor_params(
    skip: int,
    limit: int,
    distributor_ids: list[int] | None = None,
    distributor_name: str | None = None,
) -> dict:
    return {
        "skip": skip,
        "limit": limit,
        "distributor_ids": ",".join(map(str, distributor_ids))
        if distributor_ids
        else None,
        "distributor_name": distributor_name,
    }
