import ast
import json
import logging
import mimetypes
from typing import Any

import daaily.transport
from daaily.lucy.config import (
    ENTITY_ASSET_TYPE_UPLOADS_ENDPOINT_MAPPING,
    MIME_TYPE_TO_ASSET_TYPE,
    entity_type_endpoint_mapping,
)
from daaily.lucy.enums import AssetType, EntityType, MimeType
from daaily.lucy.models import Filter


def setup_logging(level=logging.INFO):
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler()],
    )


def get_entity_endpoint(base_url: str, entity_type: EntityType):
    return f"{base_url}/{entity_type_endpoint_mapping[entity_type]}"


def build_query_string(filters: list[Filter], append: bool = False) -> str:
    if append:
        query_string = "&"
    else:
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
    if "images" not in product or not isinstance(product["images"], list):
        product["images"] = []
    product["images"].append(image)
    return product


def add_image_to_product_by_blob_id(
    product: dict, image: dict, old_blob_id: str | None = None
) -> dict:
    """
    Adds or replaces images if already exists
    """
    if not image.get("blob_id"):
        raise ValueError("Image object must contain a blob")
    if "images" not in product or not isinstance(product["images"], list):
        product["images"] = []
    for i, img in enumerate(product["images"]):
        if img["blob_id"] == image["blob_id"] or img["blob_id"] == old_blob_id:
            product["images"][i] = image
            break
    else:
        product["images"].append(image)
    return product


def add_image_to_family_by_blob_id(
    family: dict, image: dict, old_blob_id: str | None = None
) -> dict:
    """
    Adds or replaces images if already exists
    """
    if not image.get("blob_id"):
        raise ValueError("Image object must contain a blob")
    if "images" not in family or not isinstance(family["images"], list):
        family["images"] = []
    for i, img in enumerate(family["images"]):
        if img["blob_id"] == image["blob_id"] or img["blob_id"] == old_blob_id:
            family["images"][i] = image
            break
    else:
        family["images"].append(image)
    return family


def add_image_to_manufacturer(man: dict, image: dict, image_type: str) -> dict:
    if f"{image_type}_image" not in man:
        raise ValueError(f"Image type {image_type} not supported")
    man[f"{image_type}_image"] = image
    return man


def add_about_to_manufacturer(man: dict, about: dict) -> dict:
    if "abouts" not in man or not isinstance(man["abouts"], list):
        man["abouts"] = []
    man["abouts"].append(about)
    return man


def gen_new_image_object(blob_id, usage: str = "pro-g"):
    return {"blob_id": blob_id, "image_usages": [usage]}


def gen_new_image_object_with_extras(blob_id, **kwargs):
    """
    Gets all of the extra args and generates a new image object
    """
    return {"blob_id": blob_id, **kwargs}


def check_field_content_set(object: dict, field: str) -> Any:
    if field in object:
        return object[field]


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


def get_file_data_and_mimetype(path: str) -> tuple[bytes, str, str]:
    try:
        with open(path, "rb") as file:
            file_data = file.read()
    except (IOError, OSError) as e:
        raise Exception(f"Failed to open file at {path}: {e}") from e
    mime_type, _ = mimetypes.guess_type(path)
    if mime_type is None:
        raise Exception(f"Could not determine content type for {path}")
    return file_data, mime_type, file.name.split("/")[-1]


def gen_new_file_object(blob_id, **kwargs):
    """
    Gets all of the extra args and generates a new file object
    """
    return {"blob_id": blob_id, **kwargs}


def add_x_goog_metadata_to_headers(metadata: dict) -> dict:
    """
    Adds the x-goog-metadata header to the headers
    """
    headers = {}
    for key, value in metadata.items():
        headers[f"x-goog-meta-{key}"] = value
    return headers


def extract_extension_from_blob_id(blob_id: str):
    return "/".join(blob_id.split("/")[:-1]).split(".")[-1]


def extract_mime_type_from_extension(extension: str) -> str | None:
    mime_type = MimeType.extract_from_extension(extension)
    if mime_type:
        return mime_type.value


def deter_duplicate_key_from_error_message(
    binary_data: bytes,
) -> tuple[str | None, str | None]:
    """
    Extracts the index name and duplicate key value from a duplicate key
    error message in binary form.

    This function decodes a binary error message and retrieves both the index
    name and the duplicate key value from the error description. For example,
    given an error message like:

        {"title": "Duplicate key found", "description": "{'index': 0, 'code': 11000,
        'errmsg': 'E11000 duplicate key error collection: lucy-dev.attributes
        index: name_1 dup key: { name: \"feature_backrest_fixed\" }', 'keyPattern':
        {'name': 1}, 'keyValue': {'name': 'feature_backrest_fixed'}}",
        "identifier_field": null, "identifier": null}'

    it will return ("attribute_id_1", "1024").

    Args:
        binary_data (bytes): A binary string containing the error message with
            duplicate key details.

    Returns:
        tuple[str, str] | None: A tuple containing the index name and the
            duplicate key value if found; otherwise, None.

    Example:
        ```python
        # Extract the duplicate key index name and value from the error message
        result = deter_duplicate_key_from_error_message(resp.data)
        if result:
            index_name, dup_value = result
            print(f"Index: {index_name}, Duplicate value: {dup_value}")
        ```
    """
    try:
        data = json.loads(binary_data.decode("utf-8"))
        description_str = data.get("description", "")
        try:
            description_data = json.loads(description_str)
        except json.JSONDecodeError:
            description_data = ast.literal_eval(description_str)
        key_value = description_data.get("keyValue", {})
        value = key_value.get("name")
        if value is not None:
            return "name", value
    except Exception:
        pass
    return None, None
