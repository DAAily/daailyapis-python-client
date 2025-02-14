import json
import mimetypes
import re
from typing import Any, Dict, Generator, Literal

import urllib3

from daaily.lucy.constants import COUNTRY_CODE_TO_COUNTRY_ID_MAPPING
from daaily.lucy.enums import EntityType
from daaily.lucy.models import Filter
from daaily.lucy.response import Response
from daaily.lucy.utils import (
    add_about_to_manufacturer,
    add_image_to_manufacturer,
    check_field_content_set,
    extract_extension_from_blob_id,
    extract_mime_type_from_extension,
    gen_new_image_object_with_extras,
    get_file_data_and_mimetype,
)

from . import BaseResource

MANUFACTURER_IMAGE_UPLOAD_ENDPOINT = "/manufacturers/{manufacturer_id}/image/upload"
MANUFACTURER_ABOUT_IMAGE_UPLOAD_ENDPOINT = (
    "/manufacturers/{manufacturer_id}/about/upload"
)

http = urllib3.PoolManager()  # for handling HTTP requests without auth


class ManufacturersResource(BaseResource):
    def get(
        self, filters: list[Filter] | None = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Retrieves manufacturers with optional filtering, returning them as a generator
        that yields each manufacturer one at a time.

        Available filters:
            - manufacturer_ids (str): Filter by comma separated manufacturer IDs.
            - manufacturer_name (str): Filter by manufacturer name.
            - status (str): Filter by status. Can hold multiple values as a comma
                separated string eg. "online,preview".
                Possible values: online, preview, offline, deleted

        Note that the following filters are automatically added to the query:
            - skip (int): Number of records to skip.
            - limit (int): Maximum number of records to retrieve.

        Args:
            filters (list[Filter] | None): A list of filters to apply to the query.

        Yields:
            dict: A dictionary representing a single manufacturer.

        Example:
            ```python
            # Define filters
            filters = [Filter("manufacturer_ids", "3100099,3100100,3100101")]

            # Get manufacturers (pagination handled internally)
            manufacturers = client.manufacturers.get(filters=filters)

            # Iterate over the results without worrying about pagination
            for m in manufacturers:
                print(f"ID: {m['manufacturer_id']}, Name: {m['name']}")
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
            response = self._client.get_entities(EntityType.MANUFACTURER, filters)
            if response.status != 200:
                break
            for item in response.json():  # type: ignore
                yield item
            skip = int(skip_filter.value) + int(limit_filter.value)
            skip_filter.value = str(skip)
            filters = [f for f in filters if f.name != "skip"]
            filters.append(skip_filter)

    def get_by_id(self, manufacturer_id: int):
        return self._client.get_entity(EntityType.MANUFACTURER, manufacturer_id)

    def get_by_domain(self, domain: str):
        return self._client.get_entity_custom(EntityType.MANUFACTURER, domain, "domain")

    def update(self, manufacturers: list[dict], filters: list[Filter] | None = None):
        return self._client.update_entities(
            EntityType.MANUFACTURER, manufacturers, filters
        )

    def create(self, manufacturers: list[dict], filters: list[Filter] | None = None):
        return self._client.create_entities(
            EntityType.MANUFACTURER, manufacturers, filters
        )

    def upload_image(  # noqa: C901
        self,
        manufacturer_id: int,
        image_type: Literal["logo", "header"],
        image_path: str | None = None,
        image_bytes: bytes | None = None,
        mime_type: str | None = None,
        filename: str | None = None,
        **kwargs,
    ) -> Any:
        """
        Uploads an image file to a manufacturer and returns the blob ID.
        Does not add the image file to the manufacturer.

        Args:
            manufacturer_id (int): The unique identifier of the manufacturer.
            image_type (str): The type of image to be uploaded (e.g., "logo", "header").
            image_path (str | None): The local file path to the image file.
            image_bytes (bytes | None): The binary data of the image file.
            mime_type (str | None): The MIME type of the image file.
            filename (str | None): The name of the image file.
            **kwargs: Additional keyword arguments containing image metadata.

        Returns:
            Any: The response data from the server.
            For example:
                {
                    "image_blob_id": "m-on/310089/manufacturers/12345/image/file.jpg",
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
            response = client.manufacturers.upload_image(
                manufacturer_id=12345,
                image_path="/path/to/image_file.jpg"
            )

            # Upload an image file using binary data
            response = client.manufacturers.upload_image(
                manufacturer_id=12345,
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
        response = self._client.get_entity(EntityType.MANUFACTURER, manufacturer_id)
        if response.status != 200:
            raise Exception(
                f"Failed to retrieve manufacturer. Status code: {response.status}. "
                + f"{response.data}"
            )
        manufacturer = response.json()
        if not manufacturer:
            raise Exception("Could not deserialize manufacturer")
        if kwargs:
            headers = dict(item for item in kwargs.items() if isinstance(item[1], str))
        else:
            headers = {}
        old_image = check_field_content_set(
            manufacturer,
            f"{image_type}_image",
        )
        if kwargs:
            headers = dict(item for item in kwargs.items() if isinstance(item[1], str))
        else:
            headers = {}
        image_upload_url = MANUFACTURER_IMAGE_UPLOAD_ENDPOINT.format(
            manufacturer_id=manufacturer_id
        )
        url = f"{self._client._base_url}{image_upload_url}?image_type={image_type}"
        if old_image:
            old_extension = extract_extension_from_blob_id(old_image["blob_id"])
            old_mime_type = extract_mime_type_from_extension(old_extension)
            if old_mime_type == content_type:
                url += f"&old_blob_id={old_image['blob_id']}"
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
        manufacturer_id: int,
        image_type: Literal["logo", "header"],
        image_path: str | None = None,
        image_url: str | None = None,
        old_blob_id: str | None = None,
        **kwargs,
    ) -> Response:
        """
        Adds or updates a manufacturer image.

        This function handles the addition or update of a manufacturer image. When
        updating an image, an old blob ID must be provided. When creating a new image,
        either an image_path or an image_url must be provided. To replace the image
        file, both an image_path (or image_url) and the old_blob_id must be provided.
        Only one of image_path or image_url should be supplied.

        The image can be provided in one of two ways:
            - As a local file using 'image_path'
            - As a remote file using 'image_url'

        The following keys may be included in the kwargs dictionary:

            - blob_id (str): The blob ID of the image.
            - direct_link (dict | None): Dictionary containing the direct link to the
                image.
            - description (str | None): Description of the image.
            - color (dict | None): Dictionary containing the color details of the image.

        Args:
            manufacturer_id (int): The unique identifier of the manufacturer.
            image_type (str): The type of image to be uploaded (e.g., "logo", "header").
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
            Exception: If the manufacturer retrieval fails.
            Exception: If the manufacturer deserialization fails.
            Exception: If the old_blob_id does not match the blob_id in the image object
            Exception: If the image download (from image_url) or upload fails.
            ValueError: If the image object does not contain a blob_id.

        Returns:
            Any: The updated manufacturer object.

        Example:
            ```python
            # Define image details
            image_data = {
                "direct_link": {"url": "https://example.com/image.jpg"},
                "description": "A sample manufacturer image",
            }

            # Add a new manufacturer image using a local file
            response = client.manufacturers.add_or_update_image(
                manufacturer_id=12345,
                image_path="/path/to/image.jpg",
                **image_data
            )

            # Add a new manufacturer image using a URL
            response = client.manufacturers.add_or_update_image(
                manufacturer_id=12345,
                image_url="https://example.com/image.jpg",
                **image_data
            )

            # Update an existing manufacturer image (without replacing the image file)
            response = client.manufacturers.add_or_update_image(
                manufacturer_id=12345,
                old_blob_id="existing-blob-id",
                **image_data
            )

            # Replace an existing manufacturer image with a new one using a local file
            response = client.manufacturers.add_or_update_image(
                manufacturer_id=12345,
                image_path="/path/to/new_image.jpg",
                old_blob_id="existing-blob-id",
                **image_data
            )

            # Replace an existing manufacturer image with a new one using a URL
            response = client.manufacturers.add_or_update_image(
                manufacturer_id=12345,
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
        response = self._client.get_entity(EntityType.MANUFACTURER, manufacturer_id)
        if response.status != 200:
            raise Exception(
                f"Failed to retrieve manufacturer. Status code: {response.status}. "
                + f"{response.data}"
            )
        manufacturer = response.json()
        if not manufacturer:
            raise Exception("Could not deserialize manufacturer")
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
                if not disposition:
                    raise ValueError(
                        "The 'content-disposition' header is missing in the response "
                        + "when trying to download image from image url"
                    )
                filename = re.findall("filename=(.+)", disposition)[0]
            resp_data = self.upload_image(
                manufacturer_id=manufacturer_id,
                image_type=image_type,
                image_path=image_path,
                image_bytes=image_data,
                mime_type=content_type,
                filename=filename,
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
        manufacturer = add_image_to_manufacturer(
            manufacturer,
            image,
            image_type,
        )
        return self._client.update_entity(EntityType.MANUFACTURER, manufacturer)

    def add_address(
        self,
        manufacturer_id: int,
        address: dict,
        country_code: str | None,
        country_of_user_code: str | None = None,
    ) -> Response:
        """
        Adds an address to a manufacturer.

        This method adds a new address to the manufacturer's information. The address
        is expected to be a dictionary with several key-value pairs, which define the
        address details. The country code is used to map the address to the correct
        country ID.

        Args:
            manufacturer_id (int): The ID of the manufacturer to which the address will
                be added.
            address (dict): The address to be added. The dictionary should include the
                following keys:
                - address_type (str|ENUM): The address type, e.g., "headquarter";
                    "country_representation"; "location".
                - status (str|ENUM): The status of the address, e.g., "online" or
                    "deleted".
                - street (str | None): The street address.
                - city (str | None): The city of the address.
                - zip (str | None): The postal code.
                - zip_box (str | None): The postal box code (if any).
                - phone (str | None): The phone number associated with the address.
                - homepage (str | None): The homepage URL associated with the address.
                - distribution_partner (str | None): The distribution partner's website
                    (if applicable).
                - name (str | None): The name of the contact person.
                - contact_email (str): The contact person's email address.
                - contact_language (str | None): The language preference of the contact
                    person (e.g., "de").
            country_code (str | None): The country code that maps to a valid country ID.

        Raises:
            ValueError: If the provided country code is invalid or not found in the
                country code mapping.
            Exception: If the manufacturer cannot be retrieved or updated.

        Returns:
            None: This method modifies the manufacturer's address in place.

        Example:
            ```python
            # Define manufacturer ID and address
            man_id = 12345
            address = {
                "address_type": "headquarter",
                "status": "online",
                "street": "123 Main St",
                "city": "Berlin",
                "zip": "10115",
                "zip_box": "PO Box 123",
                "phone": "+49 123 456789",
                "homepage": "http://manufacturer.com",
                "distribution_partner": "http://distributor.com",
                "name": "John Doe",
                "contact_email": "john.doe@manufacturer.com",
                "contact_language": "de",
            }

            # Add address to manufacturer
            client.manufacturers.add_address(man_id, address, "DE")
            ```
        """
        country_id = COUNTRY_CODE_TO_COUNTRY_ID_MAPPING.get(country_code)
        if country_id is None:
            raise ValueError(
                f"Invalid country code: {country_code}. "
                + f"Must be one of: {COUNTRY_CODE_TO_COUNTRY_ID_MAPPING.keys()}"
            )
        address["country_id"] = country_id
        if country_of_user_code:
            country_of_user_id = COUNTRY_CODE_TO_COUNTRY_ID_MAPPING.get(
                country_of_user_code
            )
            if country_of_user_id is None:
                raise ValueError(
                    f"Invalid country code: {country_of_user_code}. "
                    + f"Must be one of: {COUNTRY_CODE_TO_COUNTRY_ID_MAPPING.keys()}"
                )
            address["country_of_user_id"] = country_of_user_id
        response = self._client.get_entity(EntityType.MANUFACTURER, manufacturer_id)
        if response.status != 200:
            raise Exception(f"Failed to get manufacturer: {response.data}")
        m = response.json()
        if not m:
            raise Exception(f"Manufacturer with ID {manufacturer_id} not found.")
        if "addresses" not in m:
            m["addresses"] = []
        elif address["address_type"] == "headquarter":
            m["addresses"] = [
                a for a in m["addresses"] if a["address_type"] != "headquarter"
            ]
        m["addresses"].append(address)
        return self._client.update_entity(EntityType.MANUFACTURER, m)

    def add_new_image_by_path(
        self,
        manufacturer_id: int,
        image_path: str,
        image_type: Literal["logo", "header"],
        image_description: str | None = None,
        **kwargs,
    ) -> Response:
        """
        Adds an image to a manufacturer by uploading the image from a specified file
        path.

        This method reads the image file, determines its MIME type, and uploads it to a
        lucy and then afterwards adds it to the image object on the manufacturer.

        Args:
            manufacturer_id (int): The ID of the manufacturer to which the image will
                be added.
            image_path (str): The file path of the image to be uploaded.
            image_type (str): The type of image to be uploaded (e.g., "logo", "header").
            image_description (str | None): Optional description of the image.
            kwargs (dict | None): Optional fields and metadata add to the image.

        Raises:
            Exception: If the content type of the image cannot be determined or if the
            signed URL request fails.
            Exception: If the manufacturer cannot be retrieved or updated.

        Returns:
            dict: The updated manufacturer information after adding the image.

        Example:
            ```python
            # Define manufacturer ID and image path
            man_id = 12345
            image_path = "/path/to/image.jpg"

            # Add image to manufacturer
            man = client.manufacturers.add_new_image_by_path(man_id, image_path, "logo")

            # Print updated manufacturer information
            print(man)
            ```
        """
        try:
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
        except (IOError, OSError) as e:
            raise Exception(f"Failed to open image file at {image_path}: {e}") from e
        content_type, _ = mimetypes.guess_type(image_path)
        if content_type is None:
            raise Exception(f"Could not determine content type for {image_path}")
        if not content_type.startswith("image/"):
            raise Exception(
                f"File at {image_path} is not an image. Detected: {content_type}"
            )
        manufacturer = self._client.get_entity(EntityType.MANUFACTURER, manufacturer_id)
        if manufacturer.status != 200:
            raise Exception(f"Failed to get manufacturer: {manufacturer.data}")
        old_image = check_field_content_set(
            manufacturer.json(),  # type: ignore
            f"{image_type}_image",
        )
        if kwargs:
            headers = dict(item for item in kwargs.items() if isinstance(item[1], str))
        else:
            headers = {}
        man_image_upload_url = MANUFACTURER_IMAGE_UPLOAD_ENDPOINT.format(
            manufacturer_id=manufacturer_id
        )
        url = f"{self._client._base_url}{man_image_upload_url}?image_type={image_type}"
        if old_image:
            url += f"&old_blob_id={old_image['blob_id']}"
        resp = self._client._do_request(
            "POST",
            url,
            fields={
                "file": (image_path.split("/")[-1:][0], image_data, content_type),
            },
            headers=headers,
        )
        if resp.status != 200:
            raise Exception(
                f"Failed to upload image. Status code: {resp.status}. {resp.data}"
            )
        resp_data = json.loads(resp.data.decode("utf-8"))
        new_image = gen_new_image_object_with_extras(
            resp_data["image_blob_id"],
            size=resp_data["image_size"],
            height=resp_data["image_height"],
            width=resp_data["image_width"],
            file_type=resp_data["image_mime_type"],
            description=image_description,
            **kwargs,
        )
        manufacturer = add_image_to_manufacturer(
            manufacturer.json(),  # type: ignore
            new_image,
            image_type,
        )
        return self._client.update_entity(EntityType.MANUFACTURER, manufacturer)

    def add_about(  # noqa: C901
        self,
        manufacturer_id: int,
        about: dict,
        content_type: Literal["text", "picture", "video", "quote", "link", "pre_text"],
        image_path: str | None = None,
    ) -> Response:
        """
        Adds an about section to a manufacturer.

        This method adds or updates the "about" section in a manufacturer's profile.
        The content of the about section is provided as a dictionary and its structure
        depends on the specified content_type. The following keys may be included in the
        about dictionary:

            - status (str): The status of the about section, e.g., "online".
            - title_en (str): Title in English.
            - title_de (str): Title in German.
            - title_it (str): Title in Italian.
            - title_es (str): Title in Spanish.
            - title_fr (str): Title in French.
            - text_en (str): Description text in English.
            - text_de (str): Description text in German.
            - text_it (str): Description text in Italian.
            - text_es (str): Description text in Spanish.
            - text_fr (str): Description text in French.
            - list_order (int): The display order of the about section.
            - video_source (str): (Required for content_type "video") Video platform,
                e.g., "youtube" or "vimeo".
            - video_key (str): (Required for content_type "video") Unique identifier for
                the video.

        When the content_type is "video", the about dictionary must include both
        video_source and video_key. For content_type "picture", an image file must be
        provided via the image_path parameter, and the about dictionary should not
        contain video_key or video_source.

        Args:
            manufacturer_id (int): ID of the manufacturer to which about will be added.
            about (dict): A dictionary containing about section details. Expected keys:
                - "status": "online"
                - "title_en": "string"
                - "title_de": "string"
                - "title_it": "string"
                - "title_es": "string"
                - "title_fr": "string"
                - "text_en": "string"
                - "text_de": "string"
                - "text_it": "string"
                - "text_es": "string"
                - "text_fr": "string"
                - "list_order": 1
                - "video_source": "youtube" (for video type)
                - "video_key": "string" (for video type)
            content_type (Literal["text","picture","video","quote","link","pre_text"]):
                The type of content for the about section.
            image_path (str | None): The file path of the image to be uploaded when
                content_type is "picture".

        Raises:
            ValueError: If content_type is "video" and either video_key or video_source
                is missing, if content_type is "picture" and image_path is not provided,
                or if video-related keys are present when content_type is "picture".
            Exception: If there is an error opening the image file, determining its MIME
                type, or retrieving/updating the manufacturer.

        Returns:
            Response: The response object from updating the manufacturer with the new
                about section.

        Example:
            ```python
            # Define about section details for a text-based about section
            about_data = {
                "status": "online",
                "title_en": "About Our Company",
                "title_de": "Über unser Unternehmen",
                "title_it": "Chi siamo",
                "title_es": "Sobre nosotros",
                "title_fr": "À propos",
                "text_en": "Information in English",
                "text_de": "Information in German",
                "text_it": "Information in Italian",
                "text_es": "Information in Spanish",
                "text_fr": "Information in French",
                "list_order": 1,
            }
            response = client.manufacturers.add_about(
                manufacturer_id=12345,
                about=about_data,
                content_type="text"
            )

            # Define about section details for a video-based about section
            about_data["video_source"] = "youtube"
            about_data["video_key"] = "abc123"
            response = client.manufacturers.add_about(
                manufacturer_id=12345,
                about=about_data,
                content_type="video"
            )

            # Define about section details for a picture-based about section
            # Note: video_source and video_key should not be included when using
            # "picture" content type.
            response = client.manufacturers.add_about(
                manufacturer_id=12345,
                about=about_data,
                content_type="picture",
                image_path="/path/to/image.jpg"
            )
            ```
        """
        if content_type == "video":
            if not about.get("video_key") or not about.get("video_source"):
                raise ValueError("Video key is required for content type 'video'")
        if content_type == "picture":
            if about.get("video_key") or about.get("video_source"):
                raise ValueError(
                    "Video key and source are not allowed for content type 'picture'"
                )
            if not image_path:
                raise ValueError("Image path is required for content type 'picture'")
            try:
                with open(image_path, "rb") as image_file:
                    image_data = image_file.read()
            except (IOError, OSError) as e:
                raise Exception(
                    f"Failed to open image file at {image_path}: {e}"
                ) from e
            mime_type, _ = mimetypes.guess_type(image_path)
            if mime_type is None:
                raise Exception(f"Could not determine content type for {image_path}")
            if not mime_type.startswith("image/"):
                raise Exception(
                    f"File at {image_path} is not an image. Detected: {mime_type}"
                )
            man_image_upload_url = MANUFACTURER_ABOUT_IMAGE_UPLOAD_ENDPOINT.format(
                manufacturer_id=manufacturer_id
            )
            url = f"{self._client._base_url}{man_image_upload_url}"
            resp = self._client._do_request(
                "POST",
                url,
                fields={
                    "file": (image_path.split("/")[-1:][0], image_data, mime_type),
                },
            )
            if resp.status != 200:
                raise Exception(
                    f"Failed to upload image. Status code: {resp.status}. {resp.data}"
                )
            resp_data = json.loads(resp.data.decode("utf-8"))
            new_image = gen_new_image_object_with_extras(
                resp_data["image_blob_id"],
                size=resp_data["image_size"],
                height=resp_data["image_height"],
                width=resp_data["image_width"],
                file_type=resp_data["image_mime_type"],
            )
            about["image"] = new_image
        about["content_type"] = content_type
        response = self._client.get_entity(EntityType.MANUFACTURER, manufacturer_id)
        if response.status != 200:
            raise Exception(f"Failed to get manufacturer: {response.data}")
        m = response.json()
        if not m:
            raise Exception(f"Manufacturer with ID {manufacturer_id} not found.")
        m = add_about_to_manufacturer(m, about)
        return self._client.update_entity(EntityType.MANUFACTURER, m)
