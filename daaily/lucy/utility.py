from urllib import parse

from daaily.enums import Environment
from daaily.lucy.enums import LucyEndpoint, Status


def gen_lucy_v2_endpoint_url(environment: Environment, endpoint: LucyEndpoint) -> str:
    if environment == Environment.PRODUCTION:
        return f"https://lucy.daaily.com/api/v2{endpoint.value}"
    return f"https://lucy.staging.daaily.com/api/v2{endpoint.value}"


def gen_lucy_graphql_endpoint_url(
    environment: Environment, endpoint: LucyEndpoint
) -> str:
    if environment == Environment.PRODUCTION:
        return f"https://lucy.daaily.com/api/graphql{endpoint.value}"
    return f"https://lucy.staging.daaily.com/api/graphql{endpoint.value}"


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


def gen_graphql_payload_with_query(query: str, variables: dict | None = None) -> dict:
    if variables is None:
        variables = {}
    return {"query": query, "variables": variables}


def gen_graphql_query_params(
    skip: int, limit: int, statuses: list[Status]
) -> tuple[str, str, str]:
    status__in = ",".join(map(str, [s.value.upper() for s in statuses]))
    status__in_filter = f"input:{{status__in: [{status__in}]}}"
    limit_filter = f"limit: {limit}"
    skip_filter = f"skip: {skip}"
    return status__in_filter, limit_filter, skip_filter


def gen_graphql_query_fields(fields):
    def process_field(field):
        if isinstance(field, str):
            return field
        elif isinstance(field, dict):
            return ", ".join(
                f"{key} {{ {gen_graphql_query_fields(value)} }}"
                for key, value in field.items()
            )
        return ""

    return ", ".join(process_field(field) for field in fields)


def gen_graphql_endpoint_from_endpoint(endpoint: LucyEndpoint) -> str:
    return f"get_{endpoint.value[1:-1]}"


def gen_graphql_entity_query(
    endpoint: LucyEndpoint, fields: list, skip: int, limit: int, statuses: list[Status]
) -> str:
    status__in_filter, limit_filter, skip_filter = gen_graphql_query_params(
        skip, limit, statuses
    )
    query_fields = gen_graphql_query_fields(fields)
    return f"""
    {{
        {gen_graphql_endpoint_from_endpoint(endpoint)}
            ({status__in_filter} {skip_filter} {limit_filter} ) {{
                {query_fields}
            }}
    }}
    """
