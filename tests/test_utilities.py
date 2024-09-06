import os

import httpx

from daaily.enums import Environment
from daaily.fifi.enums import FifiEndpoint, FifiProcessType
from daaily.fifi.utility import gen_fifi_endpoint_url
from daaily.fifi.utility import load_auth_env_values as fifi_load_auth_env_values
from daaily.http.enums import HttpAuthType
from daaily.http.utility import add_authorization_header
from daaily.lucy.enums import LucyEndpoint, Status
from daaily.lucy.utility import (
    gen_graphql_endpoint_from_endpoint,
    gen_graphql_entity_query,
    gen_graphql_payload_with_query,
    gen_graphql_query_fields,
    gen_graphql_query_params,
    gen_lucy_graphql_endpoint_url,
    gen_lucy_v2_endpoint_url,
    gen_request_url_with_id,
    gen_request_url_with_params,
    remove_none_value_params,
)
from daaily.peggie.enums import PeggieEndpoint
from daaily.peggie.utility import gen_peggie_v1_endpoint_url
from daaily.sally.utility import (
    extract_token_detail,
    gen_get_token_url,
    gen_refresh_token_body,
    gen_refresh_token_url,
    load_auth_env_values,
)


def test_gen_fifi_endpoint_url():
    test_gen_fifi_endpoint_url = gen_fifi_endpoint_url(
        Environment.PRODUCTION, FifiProcessType.ENRICH, FifiEndpoint.PREDICT_IMAGE_TYPE
    )
    assert (
        test_gen_fifi_endpoint_url
        == "https://fifi.daaily.com/api/enrich/predict-image-type"
    )

    test_gen_fifi_endpoint_url = gen_fifi_endpoint_url(
        Environment.STAGING, FifiProcessType.IMAGES, FifiEndpoint.FIFI
    )
    assert (
        test_gen_fifi_endpoint_url == "https://fifi.staging.daaily.com/api/images/fifi"
    )


def test_fifi_load_auth_env_values():
    os.environ["FIFI_AUTH_USERNAME"] = "test_username"
    os.environ["FIFI_AUTH_PASSWORD"] = "test_password"
    username, password = fifi_load_auth_env_values()
    assert username == "test_username"
    assert password == "test_password"


def test_add_authorization_header():
    test_add_authorization_header = add_authorization_header(
        HttpAuthType.BEARER, "test_token", None
    )
    assert test_add_authorization_header == {"Authorization": "Bearer test_token"}

    test_add_authorization_header = add_authorization_header(
        HttpAuthType.BASIC, "test_token", {"test_key": "test_value"}
    )
    assert test_add_authorization_header == {
        "test_key": "test_value",
        "Authorization": "Basic test_token",
    }


def test_gen_peggie_v1_endpoint_url():
    test_gen_peggie_v1_endpoint_url = gen_peggie_v1_endpoint_url(
        Environment.PRODUCTION, PeggieEndpoint.PREDICT_IMAGE_ARCHITONIC_IDS
    )
    assert (
        test_gen_peggie_v1_endpoint_url
        == "https://peggie.daaily.com/api/v1/images/predict-image-architonic-ids"
    )

    test_gen_peggie_v1_endpoint_url = gen_peggie_v1_endpoint_url(
        Environment.STAGING, PeggieEndpoint.PREDICT_IMAGE_ENTITY_NAMES
    )
    assert (
        test_gen_peggie_v1_endpoint_url
        == "https://peggie.staging.daaily.com/api/v1/images/predict-image-entity-names"
    )


def test_load_auth_env_values():
    os.environ["DAAILY_USER_EMAIL"] = "test_email"
    os.environ["DAAILY_USER_UID"] = "test_uid"
    os.environ["DAAILY_USER_API_KEY"] = "test_api_key"
    user_email, user_uid, api_key = load_auth_env_values()
    assert user_email == "test_email"
    assert user_uid == "test_uid"
    assert api_key == "test_api_key"


def test_gen_refresh_token_url():
    test_gen_refresh_token_url = gen_refresh_token_url("test_api_key")
    assert (
        test_gen_refresh_token_url
        == "https://sally.daaily.com/api/v3/tokens/get-token-with-refresh-token?key=test_api_key"
    )


def test_gen_refresh_token_body():
    test_gen_refresh_token_body = gen_refresh_token_body(
        "test_email", "test_refresh_token"
    )
    assert test_gen_refresh_token_body == {
        "email": "test_email",
        "refresh_token": "test_refresh_token",
    }


def test_gen_get_token_url():
    test_gen_get_token_url = gen_get_token_url("test_api_key")
    assert (
        test_gen_get_token_url
        == "https://sally.daaily.com/api/v3/tokens/get-token?key=test_api_key"
    )


def test_extract_token_detail():
    response = httpx.Response(
        status_code=200,
        json={
            "id_token": "test_id_token",
            "refresh_token": "test_refresh_token",
            "expires_in": "3600",
        },
    )
    id_token, refresh_token, expires_in = extract_token_detail(response)
    assert id_token == "test_id_token"
    assert refresh_token == "test_refresh_token"
    assert expires_in == 3600


def test_gen_lucy_v2_endpoint_url():
    test_gen_lucy_v2_endpoint_url = gen_lucy_v2_endpoint_url(
        Environment.PRODUCTION, LucyEndpoint.PRODUCT
    )
    assert test_gen_lucy_v2_endpoint_url == "https://lucy.daaily.com/api/v2/products"

    test_gen_lucy_v2_endpoint_url = gen_lucy_v2_endpoint_url(
        Environment.STAGING, LucyEndpoint.MANUFACTURER
    )
    assert (
        test_gen_lucy_v2_endpoint_url
        == "https://lucy.staging.daaily.com/api/v2/manufacturers"
    )


def test_gen_lucy_graphql_endpoint_url():
    test_gen_lucy_graphql_endpoint_url = gen_lucy_graphql_endpoint_url(
        Environment.PRODUCTION, LucyEndpoint.PRODUCT
    )
    assert (
        test_gen_lucy_graphql_endpoint_url
        == "https://lucy.daaily.com/api/graphql/products"
    )

    test_gen_lucy_graphql_endpoint_url = gen_lucy_graphql_endpoint_url(
        Environment.STAGING, LucyEndpoint.MANUFACTURER
    )
    assert (
        test_gen_lucy_graphql_endpoint_url
        == "https://lucy.staging.daaily.com/api/graphql/manufacturers"
    )


def test_gen_request_url_with_id():
    test_gen_request_url_with_id = gen_request_url_with_id(
        "https://lucy.daaily.com/api/v2/products", 123
    )
    assert test_gen_request_url_with_id == "https://lucy.daaily.com/api/v2/products/123"

    test_gen_request_url_with_id = gen_request_url_with_id(
        "https://lucy.staging.daaily.com/api/v2/manufacturers", 456
    )
    assert (
        test_gen_request_url_with_id
        == "https://lucy.staging.daaily.com/api/v2/manufacturers/456"
    )


def test_remove_none_value_params():
    params = {"key1": "value1", "key2": None, "key3": "value3"}
    remove_none_value_params(params)
    assert params == {"key1": "value1", "key3": "value3"}


def test_gen_request_url_with_params():
    test_gen_request_url_with_params = gen_request_url_with_params(
        "https://lucy.daaily.com/api/v2/products", {"key1": "value1", "key2": "value2"}
    )
    assert (
        test_gen_request_url_with_params
        == "https://lucy.daaily.com/api/v2/products?key1=value1&key2=value2"
    )

    test_gen_request_url_with_params = gen_request_url_with_params(
        "https://lucy.staging.daaily.com/api/v2/manufacturers", {"key3": "value3"}
    )
    assert (
        test_gen_request_url_with_params
        == "https://lucy.staging.daaily.com/api/v2/manufacturers?key3=value3"
    )


def test_gen_graphql_payload_with_query():
    test_gen_graphql_payload_with_query = gen_graphql_payload_with_query(
        "query { products { name } }", {"key1": "value1"}
    )
    assert test_gen_graphql_payload_with_query == {
        "query": "query { products { name } }",
        "variables": {"key1": "value1"},
    }

    test_gen_graphql_payload_with_query = gen_graphql_payload_with_query(
        "query { manufacturers { name } }"
    )
    assert test_gen_graphql_payload_with_query == {
        "query": "query { manufacturers { name } }",
        "variables": {},
    }


def test_gen_graphql_query_params():
    test_gen_graphql_query_params = gen_graphql_query_params(0, 10, [Status.OFFLINE])
    assert test_gen_graphql_query_params == (
        "input:{status__in: [OFFLINE]}",
        "limit: 10",
        "skip: 0",
    )

    test_gen_graphql_query_params = gen_graphql_query_params(10, 20, [Status.ONLINE])
    assert test_gen_graphql_query_params == (
        "input:{status__in: [ONLINE]}",
        "limit: 20",
        "skip: 10",
    )


def test_gen_graphql_query_fields():
    test_gen_graphql_query_fields = gen_graphql_query_fields(
        ["name", "description", "status"]
    )
    assert test_gen_graphql_query_fields == "name, description, status"

    test_gen_graphql_query_fields = gen_graphql_query_fields(
        ["name", {"details": ["color", "size"]}, "status"]
    )
    assert test_gen_graphql_query_fields == "name, details { color, size }, status"


def test_gen_graphql_endpoint_from_endpoint():
    test_gen_graphql_endpoint_from_endpoint = gen_graphql_endpoint_from_endpoint(
        LucyEndpoint.PRODUCT
    )
    assert test_gen_graphql_endpoint_from_endpoint == "get_product"

    test_gen_graphql_endpoint_from_endpoint = gen_graphql_endpoint_from_endpoint(
        LucyEndpoint.MANUFACTURER
    )
    assert test_gen_graphql_endpoint_from_endpoint == "get_manufacturer"


def test_gen_graphql_entity_query():
    test_gen_graphql_entity_query = gen_graphql_entity_query(
        LucyEndpoint.PRODUCT, ["name", "description", "status"], 0, 10, [Status.ONLINE]
    )
    assert (
        test_gen_graphql_entity_query
        == """
    {
        get_product
            (input:{status__in: [ONLINE]} skip: 0 limit: 10 ) {
                name, description, status
            }
    }
    """
    )
