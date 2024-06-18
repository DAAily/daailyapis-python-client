import json
from urllib import parse

from urllib3 import BaseHTTPResponse

from daaily_v2.enums import Environment, HttpResponseCode
from daaily_v2.lucy.enums import Currency, LucyEndpoint, Status


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


def get_collection_params(
    skip: int,
    limit: int,
    manufacturer_id: int | None = None,
    collection_ids: list[int] | None = None,
) -> dict:
    return {
        "skip": skip,
        "limit": limit,
        "manufacturer_id": manufacturer_id,
        "collection_ids": ",".join(map(str, collection_ids))
        if collection_ids
        else None,
    }


def get_journalist_params(
    skip: int,
    limit: int,
    journalist_ids: list[int] | None = None,
    journalist_name: str | None = None,
) -> dict:
    return {
        "skip": skip,
        "limit": limit,
        "journalist_ids": ",".join(map(str, journalist_ids))
        if journalist_ids
        else None,
        "journalist_name": journalist_name,
    }


def get_project_params(
    skip: int,
    limit: int,
    project_ids: list[int] | None = None,
) -> dict:
    return {
        "skip": skip,
        "limit": limit,
        "project_ids": ",".join(map(str, project_ids)) if project_ids else None,
    }


def get_product_params(
    skip: int,
    limit: int,
    manufacturer_id: int | None = None,
    collection_ids: list[int] | None = None,
    family_ids: list[int] | None = None,
    product_ids: list[int] | None = None,
    statuses: list[Status] | None = None,
    price_min: int | None = None,
    price_max: int | None = None,
    currency: Currency | None = None,
) -> dict:
    return {
        "skip": skip,
        "limit": limit,
        "manufacturer_id": manufacturer_id,
        "collection_ids": ",".join(map(str, collection_ids))
        if collection_ids
        else None,
        "family_ids": ",".join(map(str, family_ids)) if family_ids else None,
        "product_ids": ",".join(map(str, product_ids)) if product_ids else None,
        "status": ",".join(map(str, [s.value for s in statuses])) if statuses else None,
        "price_min": price_min,
        "price_max": price_max,
        "currency": currency.value if currency else None,
    }


def get_family_params(
    skip: int,
    limit: int,
    manufacturer_id: int | None = None,
    family_ids: list[int] | None = None,
) -> dict:
    return {
        "skip": skip,
        "limit": limit,
        "manufacturer_id": manufacturer_id,
        "family_ids": ",".join(map(str, family_ids)) if family_ids else None,
    }


def get_creator_params(
    skip: int,
    limit: int,
    creator_ids: list[int] | None = None,
) -> dict:
    return {
        "skip": skip,
        "limit": limit,
        "creator_ids": ",".join(map(str, creator_ids)) if creator_ids else None,
    }


def get_filter_params(
    skip: int,
    limit: int,
    filter_ids: list[int] | None = None,
) -> dict:
    return {
        "skip": skip,
        "limit": limit,
        "filter_ids": ",".join(map(str, filter_ids)) if filter_ids else None,
    }


def get_story_params(
    skip: int,
    limit: int,
    story_ids: list[int] | None = None,
) -> dict:
    return {
        "skip": skip,
        "limit": limit,
        "story_ids": ",".join(map(str, story_ids)) if story_ids else None,
    }


def get_group_params(
    skip: int,
    limit: int,
    group_ids: list[int] | None = None,
) -> dict:
    return {
        "skip": skip,
        "limit": limit,
        "group_ids": ",".join(map(str, group_ids)) if group_ids else None,
    }


def get_fair_params(
    skip: int,
    limit: int,
    fair_ids: list[int] | None = None,
) -> dict:
    return {
        "skip": skip,
        "limit": limit,
        "fair_ids": ",".join(map(str, fair_ids)) if fair_ids else None,
    }
