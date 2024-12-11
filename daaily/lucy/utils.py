import json
import mimetypes

import daaily.transport
from daaily.lucy.config import (
    ENTITY_ASSET_TYPE_UPLOADS_ENDPOINT_MAPPING,
    MIME_TYPE_TO_ASSET_TYPE,
    entity_type_endpoint_mapping,
)
from daaily.lucy.enums import AssetType, EntityType
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


def get_asset_type_from_mime_type(mime_type: str) -> AssetType | None:
    return MIME_TYPE_TO_ASSET_TYPE.get(mime_type, None)


def get_entity_asset_type_endpoint(
    entity_type: EntityType, entity_id: int, asset_type: AssetType
) -> str | None:
    endpoint = ENTITY_ASSET_TYPE_UPLOADS_ENDPOINT_MAPPING.get(
        (entity_type, asset_type), None
    )
    if endpoint:
        return endpoint.format(entity_id=entity_id)


def get_file_data_and_mimetype(path: str) -> tuple[bytes, str]:
    try:
        with open(path, "rb") as file:
            file_data = file.read()
    except (IOError, OSError) as e:
        raise Exception(f"Failed to open file at {path}: {e}") from e
    mime_type, _ = mimetypes.guess_type(path)
    if mime_type is None:
        raise Exception(f"Could not determine content type for {path}")
    return file_data, mime_type


def gen_new_file_object(blob_id, **kwargs):
    """
    Gets all of the extra args and generates a new file object
    """
    return {"blob_id": blob_id, **kwargs}
