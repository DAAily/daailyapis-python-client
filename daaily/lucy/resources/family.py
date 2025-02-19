import json
import os
import re
from typing import Any, Dict, Generator
from urllib.parse import urlparse

import urllib3

from daaily.lucy.constants import ENTITY_STATUS
from daaily.lucy.enums import AssetType, EntityType
from daaily.lucy.models import Filter
from daaily.lucy.response import Response
from daaily.lucy.utils import (
    add_image_to_family_by_blob_id,
    extract_extension_from_blob_id,
    extract_mime_type_from_extension,
    gen_new_image_object_with_extras,
    get_file_data_and_mimetype,
)

from . import BaseResource

FAMILY_IMAGE_UPLOAD_ENDPOINT = "/families/{family_id}/image/upload"

http = urllib3.PoolManager()  # for handling HTTP requests without auth


class FamiliesResource(BaseResource):
    def get(
        self, filters: list[Filter] | None = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Retrieves families with optional filtering, returning them as a generator
        that yields each family one at a time.

        Available filters:
            - family_ids (str): Filter by comma separated family IDs.
            - manufacturer_id (str): Filter by manufacturer ID.
            - status (str): Filter by status. Can hold multiple values as a comma
                separated string eg. "online,preview".
                Possible values: online, preview, offline, deleted

        Note that the following filters are automatically added to the query:
            - skip (int): Number of records to skip.
            - limit (int): Maximum number of records to retrieve.

        Args:
            filters (list[Filter] | None): A list of filters to apply to the query.

        Yields:
            dict: A dictionary representing a single family.

        Example:
            ```python
            # Define filters
            filters = [Filter("family_ids", "12345, 78910")]

            # Get families (pagination handled internally)
            families = client.families.get(filters=filters)

            # Iterate over the results without worrying about pagination
            for f in families:
                print(f"ID: {f['family_id']}, Name: {f['name_en']}")
            ```
        """
        if filters is None:
            filters = []
        filters = [f for f in filters if f.name not in ["limit", "skip"]]
        limit_filter = Filter(name="limit", value="100")
        skip_filter = Filter(name="skip", value="0")
        filters.append(limit_filter)
        filters.append(skip_filter)
        while True:
            response = self._client.get_entities(EntityType.FAMILY, filters)
            if response.status != 200:
                break
            for item in response.json():  # type: ignore
                yield item
            skip = int(skip_filter.value) + int(limit_filter.value)
            skip_filter.value = str(skip)
            filters = [f for f in filters if f.name != "skip"]
            filters.append(skip_filter)

    def get_by_id(self, family_id: int):
        return self._client.get_entity(EntityType.FAMILY, family_id)

    def update(self, families: list[dict], filters: list[Filter] | None = None):
        return self._client.update_entities(EntityType.FAMILY, families, filters)

    def create(self, families: list[dict], filters: list[Filter] | None = None):
        return self._client.create_entities(EntityType.FAMILY, families, filters)

    def upload_image(
        self,
        family_id: int,
        image_path: str | None = None,
        image_bytes: bytes | None = None,
        mime_type: str | None = None,
        filename: str | None = None,
        old_blob_id: str | None = None,
        **kwargs,
    ) -> Any:
        """
        Uploads an image file to a family and returns the blob ID.
        Does not add the image file to the family.

        Args:
            family_id (int): The unique identifier of the family.
            image_path (str | None): The local file path to the image file.
            image_bytes (bytes | None): The binary data of the image file.
            mime_type (str | None): The MIME type of the image file.
            filename (str | None): The name of the image file.
            old_blob_id (str | None): The blob ID of the existing image file.
            **kwargs: Additional keyword arguments containing image metadata.

        Returns:
            Any: The response data from the server.
            For example:
                {
                    "image_blob_id": "m-on/310089/families/12345/image/file.jpg",
                    "image_mime_type": "image/jpeg",
                    "image_size": 123456,
                    "image_height": 600,
                    "image_width": 800
                }

        Raises:
            Exception: If neither image_path nor image_bytes is provided.
            Exception: If the content type of the image file is not an image type.
            Exception: If the upload fails.

        Example:
            ```python
            # Upload an image file using a local file
            response = client.families.upload_image(
                family_id=12345,
                image_path="/path/to/image_file.jpg"
            )

            # Upload an image file using binary data
            response = client.families.upload_image(
                family_id=12345,
                image_bytes=b"binary_data",
                mime_type="image/jpeg",
                filename="image_file.jpg"
            )
            ```
        """
        if not image_path and not image_bytes:
            raise Exception("Either image_path or image_bytes must be provided")
        if image_path:
            image_data, content_type, filename = get_file_data_and_mimetype(image_path)
        else:
            if not mime_type:
                raise ValueError(
                    "If 'image_bytes' is provided, 'mime_type' must be specified."
                )
            image_data = image_bytes
            content_type = mime_type
        if content_type is None:
            raise Exception("Could not determine content type for image")
        if not content_type.startswith("image/"):
            raise Exception(f"File is not an image type. Detected: {content_type}")
        if kwargs:
            headers = dict(item for item in kwargs.items() if isinstance(item[1], str))
        else:
            headers = {}
        image_upload_url = FAMILY_IMAGE_UPLOAD_ENDPOINT.format(family_id=family_id)
        url = f"{self._client._base_url}{image_upload_url}"
        if old_blob_id:
            old_extension = extract_extension_from_blob_id(old_blob_id)
            old_mime_type = extract_mime_type_from_extension(old_extension)
            if old_mime_type == content_type:
                url += f"&old_blob_id={old_blob_id}"
        resp = self._client._do_request(
            "POST",
            url,
            fields={"file": (filename, image_data, content_type)},
            headers=headers,
        )
        if resp.status != 200:
            raise Exception(
                f"Failed to upload image. Status code: {resp.status}. {resp.data}"
            )
        return json.loads(resp.data.decode("utf-8"))

    def add_or_update_image(  # noqa: C901
        self,
        family_id: int,
        image_path: str | None = None,
        image_url: str | None = None,
        old_blob_id: str | None = None,
        **kwargs,
    ) -> Response:
        """
        Adds or updates a family image.

        This function handles the addition or update of a family image. When updating
        an image, an old blob ID must be provided. When creating a new image, either an
        image_path or an image_url must be provided. To replace the image file, both an
        image_path (or image_url) and the old_blob_id must be provided. Only one of
        image_path or image_url should be supplied.

        The image can be provided in one of two ways:
            - As a local file using 'image_path'
            - As a remote file using 'image_url'

        The following keys may be included in the kwargs dictionary:

            - blob_id (str): The blob ID of the image.
            - image_usages (list[str] | None): List of image usages, e.g., "fam-g",
                "fam-sq".
            - image_type (str | None): The type of image, e.g., "Cut-out image",
                "Ambient image", "Drawing image", "Material image", "Detail image".
            - list_order (int | None): The display order of the image.
            - direct_link (dict | None): Dictionary containing the direct link to the
                image.
            - description (str | None): Description of the image.
            - color (dict | None): Dictionary containing the color details of the image.

        Args:
            family_id (int): The unique identifier of the family.
            image_path (str | None): The local file path to the new image file. Required
                when creating a new image or replacing an existing image using a local
                file.
            image_url (str | None): The URL of the new image file. Required when
                creating a new image or replacing an existing image using a remote image
                source.
            old_blob_id (str | None): The blob ID of the existing image. Required when
                updating an image.
            **kwargs: Additional keyword arguments containing image metadata.

        Raises:
            ValueError: If both image_path and image_url are provided.
            Exception: If neither image_path nor image_url is provided when required,
                or if the old_blob_id is missing when updating an image.
            Exception: If the family retrieval fails.
            Exception: If the family deserialization fails.
            Exception: If the old_blob_id does not match the blob_id in the image object
            Exception: If the image download (from image_url) or upload fails.
            ValueError: If the image object does not contain a blob_id.

        Returns:
            Any: The updated family object.

        Example:
            ```python
            # Define image details
            image_data = {
                "image_usages": ["fam-g"],
                "image_type": "Cut-out image",
                "list_order": 1,
                "direct_link": {"url": "https://example.com/image.jpg"},
                "description": "A sample family image",
            }

            # Add a new family image using a local file
            response = client.families.add_or_update_image(
                family_id=12345,
                image_path="/path/to/image.jpg",
                **image_data
            )

            # Add a new family image using a URL
            response = client.families.add_or_update_image(
                family_id=12345,
                image_url="https://example.com/image.jpg",
                **image_data
            )

            # Update an existing family image (without replacing the image file)
            response = client.families.add_or_update_image(
                family_id=12345,
                old_blob_id="existing-blob-id",
                **image_data
            )

            # Replace an existing family image with a new one using a local file
            response = client.families.add_or_update_image(
                family_id=12345,
                image_path="/path/to/new_image.jpg",
                old_blob_id="existing-blob-id",
                **image_data
            )

            # Replace an existing family image with a new one using a URL
            response = client.families.add_or_update_image(
                family_id=12345,
                image_url="https://example.com/new_image.jpg",
                old_blob_id="existing-blob-id",
                **image_data
            )
            ```
        """
        if image_path and image_url:
            raise ValueError(
                "Only one of 'image_path' or 'image_url' should be provided"
            )
        if not (image_path or image_url) and not old_blob_id:
            raise Exception(
                "When updating the image an old blob id must be provided. "
                + "However, when creating a new image the image path or image url must "
                + "be provided. To replace the image file both an image path "
                + "(or image url) and the old blob id must be provided."
            )
        response = self._client.get_entity(EntityType.FAMILY, family_id)
        if response.status != 200:
            raise Exception(
                f"Failed to retrieve family. Status code: {response.status}. "
                + f"{response.data}"
            )
        family = response.json()
        if not family:
            raise Exception("Could not deserialize family")
        if (
            old_blob_id
            and kwargs.get("blob_id")
            and kwargs.get("blob_id") != old_blob_id
        ):
            raise Exception(
                "The old blob id provided does not match the blob id provided in the "
                + "image object"
            )
        image = kwargs.copy()
        if image_path or image_url:
            image_data = None
            content_type = None
            filename = None
            if image_url:
                resp = http.request("GET", image_url)
                if resp.status != 200:
                    raise Exception(
                        f"Failed to downloading image. Code: {resp.status}. {resp.data}"
                    )
                content_type = resp.headers.get("Content-Type")
                image_data = resp.data
                disposition = resp.headers.get("content-disposition")
                if disposition:
                    filename = re.findall("filename=(.+)", disposition)[0]
                else:
                    parsed_url = urlparse(image_url)
                    filename = os.path.basename(parsed_url.path)
                    if not filename:
                        raise ValueError(
                            "Could not determine filename from URL and "
                            + "'content-disposition' header is missing in the response "
                            + "when trying to download image from image url"
                        )
            resp_data = self.upload_image(
                family_id=family_id,
                image_path=image_path,
                image_bytes=image_data,
                mime_type=content_type,
                filename=filename,
                old_blob_id=old_blob_id,
                **kwargs,
            )
            new_kwargs = {k: v for k, v in kwargs.items() if k != "blob_id"}
            image = gen_new_image_object_with_extras(
                resp_data["image_blob_id"],
                size=resp_data["image_size"],
                height=resp_data["image_height"],
                width=resp_data["image_width"],
                file_type=resp_data["image_mime_type"],
                **new_kwargs,
            )
        if not image.get("blob_id"):
            raise ValueError("Image object must contain a blob_id")
        family = add_image_to_family_by_blob_id(family, image, old_blob_id=old_blob_id)
        return self._client.update_entity(EntityType.FAMILY, family)

    def change_image_status(
        self, family_id: int, blob_id: str, target_status: ENTITY_STATUS
    ) -> Response:
        """
        Changes the status of an image associated with a family.

        This function updates the status of a specified image (identified by its blob
        ID) for a given family. The status can be set to "online", "preview", or
        "deleted".

        Args:
            family_id (int): The unique identifier of the family.
            blob_id (str): The blob ID of the image whose status is to be changed.
            target_status (Literal["online", "preview", "deleted"]): The target status
                for the image.

        Returns:
            Response: Response from the server indicating the result of the operation.
            For example:
                {
                    "blob_id": "string",
                    "move_operation": "string",
                    "meta": {
                        "application": "lucy-api",
                        "topic_name": "entity-preview-staging"
                    }
                }

        Example:
            ```python
            # Change the status of an image to "online"
            response = client.families.change_image_status(
                family_id=12345,
                blob_id="m-on/310089/families/12345/image/file.jpg",
                target_status="deleted"
            )
            ```
        """
        return self._client.move_asset(
            EntityType.FAMILY, family_id, AssetType.IMAGE, blob_id, target_status
        )
