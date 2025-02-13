import json
from typing import Any, Dict, Generator

from daaily.lucy.enums import EntityType
from daaily.lucy.models import Filter
from daaily.lucy.utils import (
    add_image_to_family_by_blob_id,
    gen_new_image_object_with_extras,
    get_file_data_and_mimetype,
)

from . import BaseResource

FAMILY_IMAGE_UPLOAD_ENDPOINT = "/families/{family_id}/image/upload"


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
        old_blob_id: str | None = None,
        **kwargs,
    ) -> Any:
        """ """
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

    def add_or_update_family_image(
        self,
        family_id: int,
        image_path: str | None = None,
        old_blob_id: str | None = None,
        **kwargs,
    ):
        """
        Adds or updates a family image.

        This function handles the addition or update of a family image. When updating
        an image, an old blob ID must be provided. When creating a new image, the image
        path must be provided. To replace the image file, both the image path and the
        old blob ID must be provided.

        The following keys may be included in the kwargs dictionary:


            - blob_id (str): The blob ID of the image.
            - image_usages (list[str] | None): List of image usages eg. "pro-g", "pro-b"
            - image_type (str | None): The type of image, e.g., "Cut-out image",
                "Ambient image", "Drawing image", "Material image", "Detail image".
            - list_order (int | None): The display order of the image.
            - direct_link (dict | None): Dictionary containing the direct link to image.
            - description (str | None): Description of the image.
            - color (dict | None): Dictionary containing the color of the image.

        Args:
            family_id (int): The unique identifier of the family.
            image_path (str | None): The path to the new image file. Required when
                creating a new image or replacing an existing image.
            old_blob_id (str | None): The blob ID of the existing image. Required when
                updating an image.
            **kwargs: Additional keyword arguments containing image metadata.

        Raises:
            Exception: If the image path or old blob ID is not provided as required.
            Exception: If the family retrieval fails.
            Exception: If the family deserialization fails.
            Exception: If the old blob ID does not match the blob ID in the image object
            Exception: If the image upload fails.
            ValueError: If the image object does not contain a blob ID.

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

            # Add a new families image
            response = client.families.add_or_update_family_image(
                family_id=12345,
                image_path="/path/to/image.jpg",
                **image_data
            )

            # Update an existing family image
            response = client.families.add_or_update_family_image(
                family_id=12345,
                old_blob_id="existing-blob-id",
                **image_data
            )

            # Replace an existing family image with a new one
            response = client.families.add_or_update_family_image(
                family_id=12345,
                image_path="/path/to/new_image.jpg",
                old_blob_id="existing-blob-id",
                **image_data
            )
            ```
        """
        if not image_path and not old_blob_id:
            raise Exception(
                "When updating the image an old blob id must be provided. "
                + "However, when creating a new image the image path must be provided. "
                + "To replace the image file both the image path and the old blob id "
                + "must be provided."
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
        image = dict(kwargs.items())
        if image_path:
            resp_data = self.upload_image(
                family_id=family_id,
                image_path=image_path,
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
        return self.update([family])
