import json
from typing import Any, Dict, Generator

from daaily.lucy.enums import EntityType, Service
from daaily.lucy.models import Filter
from daaily.lucy.utils import (
    extract_extension_from_blob_id,
    extract_mime_type_from_extension,
    get_file_data_and_mimetype,
)

from .. import BaseResource

COLLECTION_IMAGE_UPLOAD_ENDPOINT = "/collections/{collection_id}/image/upload"


class CollectionsResource(BaseResource):
    def get(
        self, filters: list[Filter] | None = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Retrieves collections with optional filtering, returning them as a generator
        that yields each collection one at a time.

        Available filters:
            - manufacturer_id (int): Filter by manufacturer ID.
            - collection_ids (str): Filter by comma separated collection IDs.

        Note that the following filters are automatically added to the query:
            - skip (int): Number of records to skip.
            - limit (int): Maximum number of records to retrieve.

        Args:
            filters (list[Filter] | None): A list of filters to apply to the query.

        Yields:
            dict: A dictionary representing a single collection.

        Example:
            ```python
            # Define filters
            filters = [Filter("manufacturer_id", "12345")]

            # Get collections (pagination handled internally)
            collections = client.collections.get(filters=filters)

            # Iterate over the results without worrying about pagination
            for c in collections:
                print(f"ID: {c['collection_id']}, Name: {c['name_en']}")
            ```
        """
        if filters is None:
            filters = []
        limit_value = "100"
        skip_value = "0"
        new_filters = []
        for f in filters:
            if f.name == "limit":
                limit_value = f.value
            elif f.name == "skip":
                skip_value = f.value
            else:
                new_filters.append(f)
        limit_filter = Filter(name="limit", value=limit_value)
        skip_filter = Filter(name="skip", value=skip_value)
        new_filters.append(limit_filter)
        new_filters.append(skip_filter)
        while True:
            response = self._client.get_entities(EntityType.COLLECTION, new_filters)
            if response.status != 200:
                break
            for item in response.json():  # type: ignore
                yield item
            skip_value = str(int(skip_value) + int(limit_value))
            skip_filter.value = skip_value
            new_filters = [f for f in new_filters if f.name != "skip"]
            new_filters.append(skip_filter)

    def get_by_id(self, collection_id: int):
        return self._client.get_entity(EntityType.COLLECTION, collection_id)

    def refresh(self, collection_id: int):
        """
        This will refresh the collection data. It will not return anything but will
        simply refresh the data which will then update the denormalized data on the
        collection. It will not change the revision_uuid.
        """
        return self._client.refresh_entity(EntityType.COLLECTION, collection_id)

    def update(
        self,
        collections: list[dict],
        filters: list[Filter] | None = None,
        service: Service = Service.SPARKY,
    ):
        return self._client.update_entities(
            EntityType.COLLECTION, collections, filters, service=service
        )

    def create(
        self,
        collections: list[dict],
        filters: list[Filter] | None = None,
        service: Service = Service.SPARKY,
    ):
        return self._client.create_entities(
            EntityType.COLLECTION, collections, filters, service=service
        )

    def upload_image(
        self,
        collection_id: int,
        image_path: str | None = None,
        image_bytes: bytes | None = None,
        mime_type: str | None = None,
        filename: str | None = None,
        old_blob_id: str | None = None,
        **kwargs,
    ) -> Any:
        """
        Uploads an image file to a collection and returns the blob ID.
        Does not add the image file to the collection.

        Args:
            collection_id (int): The unique identifier of the collection.
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
                    "image_blob_id": "m-on/310089/collections/12345/image/file.jpg",
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
            response = client.collections.upload_image(
                collection_id=12345,
                image_path="/path/to/image_file.jpg"
            )

            # Upload an image file using binary data
            response = client.collections.upload_image(
                collection_id=12345,
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
        image_upload_url = COLLECTION_IMAGE_UPLOAD_ENDPOINT.format(
            collection_id=collection_id
        )
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
