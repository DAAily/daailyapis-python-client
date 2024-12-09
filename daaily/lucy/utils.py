import json

import daaily.transport
from daaily.lucy.config import entity_type_endpoint_mapping
from daaily.lucy.enums import EntityType
from daaily.lucy.models import Filter


def get_entity_endpoint(base_url: str, entity_type: EntityType):
    return f"{base_url}/{entity_type_endpoint_mapping[entity_type]}"


def build_query_string(filters: list[Filter]):
    query_string = "?"
    for filter in filters:
        query_string += f"{filter.name}={filter.value}&"
    return query_string


def get_skip_query(skip: int) -> tuple[int, int]:
    limit = 500
    lskip = limit * skip
    return lskip, limit


def handle_entity_response_data(
    response: daaily.transport.Response, entities: list[dict]
) -> tuple[list[dict], bool]:
    if response.status == 200:
        data = json.loads(response.data.decode("utf-8"))
        entities.extend(data)
        more_data = True
    else:
        more_data = False
    return entities, more_data


def add_image_to_product(product: dict, image: dict) -> dict:
    if "images" not in product:
        product["images"] = []
    product["images"].append(image)
    return product


def gen_new_image_object(blob_id, usage: str = "pro-g"):
    return {"blob_id": blob_id, "image_usages": [usage]}
