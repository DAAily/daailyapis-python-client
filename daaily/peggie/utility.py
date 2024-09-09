from daaily.enums import Environment
from daaily.peggie.enums import PeggieEndpoint


def gen_peggie_v1_endpoint_url(
    environment: Environment, endpoint: PeggieEndpoint
) -> str:
    if environment == Environment.PRODUCTION:
        return f"https://peggie.daaily.com/api/v1/images{endpoint.value}"
    return f"https://peggie.staging.daaily.com/api/v1/images{endpoint.value}"
