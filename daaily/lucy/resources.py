import json
import mimetypes
import os
from typing import TYPE_CHECKING, Any, Dict, Generator

import urllib3

from daaily.lucy.enums import EntityType
from daaily.lucy.models import Filter
from daaily.lucy.utils import (
    add_image_to_product,
    gen_new_file_object,
    gen_new_image_object,
    get_asset_type_from_mime_type,
    get_entity_asset_type_endpoint,
    get_file_data_and_mimetype,
)

if TYPE_CHECKING:
    from daaily.lucy.client import Client

PRODUCT_SIGNED_URL_ENDPOINT = "/products/{product_id}/images/online"
FILE_UPLOADS_UNSPECIFIC_ENDPOINT = "/files/uploads/temp/unspecific"

http = urllib3.PoolManager()  # for handling HTTP requests without auth


class BaseResource:
    def __init__(self, client: "Client"):
        self._client: "Client" = client

    def get(self, filters: list[Filter] | None = None):
        raise NotImplementedError

    def get_by_id(self, entity_id: int):
        raise NotImplementedError

    def update(self, data: list[dict], filters: list[Filter] | None = None):
        raise NotImplementedError

    def create(self, data: list[dict], filters: list[Filter] | None = None):
        raise NotImplementedError


class ManufacturersResource(BaseResource):
    def get(
        self, filters: list[Filter] | None = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Retrieves manufacturers with optional filtering, returning them as a generator
        that yields each manufacturer one at a time.

        Available filters:
            - manufacturer_ids (str): Filter by comma seperated manufacturer IDs.
            - manufacturer_name (str): Filter by manufacturer name.

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


class DistributorsResource(BaseResource):
    def get(
        self, filters: list[Filter] | None = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Retrieves distributors with optional filtering, returning them as a generator
        that yields each distributor one at a time.

        Available filters:
            - distributor_ids (str): Filter by comma separated distributor IDs.
            - distributor_name (str): Filter by regex name search.

        Note that the following filters are automatically added to the query:
            - skip (int): Number of records to skip.
            - limit (int): Maximum number of records to retrieve.

        Args:
            filters (list[Filter] | None): A list of filters to apply to the query.

        Yields:
            dict: A dictionary representing a single distributor.

        Example:
            ```python
            # Define filters
            filters = [Filter("distributor_name", "minotti munich")]

            # Get distributors (pagination handled internally)
            distributors = client.distributors.get(filters=filters)

            # Iterate over the results without worrying about pagination
            for d in distributors:
                print(f"ID: {d['distributor_id']}, Name: {d['name']}")
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
            response = self._client.get_entities(EntityType.DISTRIBUTOR, filters)
            if response.status != 200:
                break
            for item in response.json():  # type: ignore
                yield item
            skip = int(skip_filter.value) + int(limit_filter.value)
            skip_filter.value = str(skip)
            filters = [f for f in filters if f.name != "skip"]
            filters.append(skip_filter)

    def get_by_id(self, distributor_id: int):
        return self._client.get_entity(EntityType.DISTRIBUTOR, distributor_id)

    def update(self, distributors: list[dict], filters: list[Filter] | None = None):
        return self._client.update_entities(
            EntityType.DISTRIBUTOR, distributors, filters
        )

    def create(self, distributors: list[dict], filters: list[Filter] | None = None):
        return self._client.create_entities(
            EntityType.DISTRIBUTOR, distributors, filters
        )


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
        filters = [f for f in filters if f.name not in ["limit", "skip"]]
        limit_filter = Filter(name="limit", value="100")
        skip_filter = Filter(name="skip", value="0")
        filters.append(limit_filter)
        filters.append(skip_filter)
        while True:
            response = self._client.get_entities(EntityType.COLLECTION, filters)
            if response.status != 200:
                break
            for item in response.json():  # type: ignore
                yield item
            skip = int(skip_filter.value) + int(limit_filter.value)
            skip_filter.value = str(skip)
            filters = [f for f in filters if f.name != "skip"]
            filters.append(skip_filter)

    def get_by_id(self, collection_id: int):
        return self._client.get_entity(EntityType.COLLECTION, collection_id)

    def update(self, collections: list[dict], filters: list[Filter] | None = None):
        return self._client.update_entities(EntityType.COLLECTION, collections, filters)

    def create(self, collections: list[dict], filters: list[Filter] | None = None):
        return self._client.create_entities(EntityType.COLLECTION, collections, filters)


class JournalistsResource(BaseResource):
    def get(
        self, filters: list[Filter] | None = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Retrieves journalists with optional filtering, returning them as a generator
        that yields each journalist one at a time.

        Available filters:
            - journalist_ids (str): Filter by comma separated journalist IDs.

        Note that the following filters are automatically added to the query:
            - skip (int): Number of records to skip.
            - limit (int): Maximum number of records to retrieve.

        Args:
            filters (list[Filter] | None): A list of filters to apply to the query.

        Yields:
            dict: A dictionary representing a single journalist.

        Example:
            ```python
            # Define filters
            filters = [Filter("journalist_ids", "12345, 12322")]

            # Get journalists (pagination handled internally)
            journalists = client.journalists.get(filters=filters)

            # Iterate over the results without worrying about pagination
            for j in journalists:
                print(f"ID: {j['journalist_id']}, Name: {j['name']}")
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
            response = self._client.get_entities(EntityType.JOURNALIST, filters)
            if response.status != 200:
                break
            for item in response.json():  # type: ignore
                yield item
            skip = int(skip_filter.value) + int(limit_filter.value)
            skip_filter.value = str(skip)
            filters = [f for f in filters if f.name != "skip"]
            filters.append(skip_filter)

    def get_by_id(self, journalist_id: int):
        return self._client.get_entity(EntityType.JOURNALIST, journalist_id)

    def update(self, journalists: list[dict], filters: list[Filter] | None = None):
        return self._client.update_entities(EntityType.JOURNALIST, journalists, filters)

    def create(self, journalists: list[dict], filters: list[Filter] | None = None):
        return self._client.create_entities(EntityType.JOURNALIST, journalists, filters)


class MaterialsResource(BaseResource):
    def get(
        self, filters: list[Filter] | None = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Retrieves materials with optional filtering, returning them as a generator
        that yields each material one at a time.

        Available filters:
            - manufacturer_id (int): Filter by manufacturer ID.
            - material_ids (str): Filter by comma separated material IDs.

        Note that the following filters are automatically added to the query:
            - skip (int): Number of records to skip.
            - limit (int): Maximum number of records to retrieve.

        Args:
            filters (list[Filter] | None): A list of filters to apply to the query.

        Yields:
            dict: A dictionary representing a single material.

        Example:
            ```python
            # Define filters
            filters = [Filter("manufacturer_id", "12345")]

            # Get materials (pagination handled internally)
            materials = client.materials.get(filters=filters)

            # Iterate over the results without worrying about pagination
            for m in materials:
                print(f"ID: {m['material_id']}, Name: {m['name_en']}")
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
            response = self._client.get_entities(EntityType.MATERIAL, filters)
            if response.status != 200:
                break
            for item in response.json():  # type: ignore
                yield item
            skip = int(skip_filter.value) + int(limit_filter.value)
            skip_filter.value = str(skip)
            filters = [f for f in filters if f.name != "skip"]
            filters.append(skip_filter)

    def get_by_id(self, material_id: int):
        return self._client.get_entity(EntityType.MATERIAL, material_id)

    def update(self, materials: list[dict], filters: list[Filter] | None = None):
        return self._client.update_entities(EntityType.MATERIAL, materials, filters)

    def create(self, materials: list[dict], filters: list[Filter] | None = None):
        return self._client.create_entities(EntityType.MATERIAL, materials, filters)


class ProjectsResource(BaseResource):
    def get(
        self, filters: list[Filter] | None = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Retrieves project with optional filtering, returning them as a generator
        that yields each project one at a time.

        Available filters:
            - project_ids (str): Filter by comma separated project IDs.

        Note that the following filters are automatically added to the query:
            - skip (int): Number of records to skip.
            - limit (int): Maximum number of records to retrieve.

        Args:
            filters (list[Filter] | None): A list of filters to apply to the query.

        Yields:
            dict: A dictionary representing a single project.

        Example:
            ```python
            # Define filters
            filters = [Filter("manufacturer_id", "12345")]

            # Get materials (pagination handled internally)
            projects = client.projects.get(filters=filters)

            # Iterate over the results without worrying about pagination
            for p in projects:
                print(f"ID: {p['project_id']}, Name: {p['name']}")
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
            response = self._client.get_entities(EntityType.PROJECT, filters)
            if response.status != 200:
                break
            for item in response.json():  # type: ignore
                yield item
            skip = int(skip_filter.value) + int(limit_filter.value)
            skip_filter.value = str(skip)
            filters = [f for f in filters if f.name != "skip"]
            filters.append(skip_filter)

    def get_by_id(self, project_id: int):
        return self._client.get_entity(EntityType.PROJECT, project_id)

    def update(self, projects: list[dict], filters: list[Filter] | None = None):
        return self._client.update_entities(EntityType.PROJECT, projects, filters)

    def create(self, projects: list[dict], filters: list[Filter] | None = None):
        return self._client.create_entities(EntityType.PROJECT, projects, filters)


class ProductsResource(BaseResource):
    def get(
        self, filters: list[Filter] | None = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Retrieves products with optional filtering, returning them as a generator
        that yields each product one at a time.

        Available filters:
            - manufacturer_id (int): Filter by manufacturer ID.
            - collection_ids (str): Filter by comma separated collection IDs.
            - family_ids (str): Filter by comma separated family IDs.
            - product_ids (str): Filter by comma separated product IDs.
            - status (str): Filter by product status (online, preview, offline, deleted)
            - price_min (float): Filter by minimum price.
            - price_max (float): Filter by maximum price.
            - currency (str): Filter by currency (chf, eur, gbp, usd).

        Note that the following filters are automatically added to the query:
            - skip (int): Number of records to skip.
            - limit (int): Maximum number of records to retrieve.

        Args:
            filters (list[Filter] | None): A list of filters to apply to the query.

        Yields:
            dict: A dictionary representing a single product.

        Example:
            ```python
            # Define filters
            filters = [Filter("manufacturer_id", "12345"), Filter("status", "online")]

            # Get products (pagination handled internally)
            products = client.products.get(filters=filters)

            # Iterate over the results without worrying about pagination
            for p in products:
                print(f"ID: {p['product_id']}, Name: {p['name']}")
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
            response = self._client.get_entities(EntityType.PRODUCT, filters)
            if response.status != 200:
                break
            for item in response.json():  # type: ignore
                yield item
            skip = int(skip_filter.value) + int(limit_filter.value)
            skip_filter.value = str(skip)
            filters = [f for f in filters if f.name != "skip"]
            filters.append(skip_filter)

    def get_by_id(self, product_id: int):
        return self._client.get_entity(EntityType.PRODUCT, product_id)

    def update(self, products: list[dict], filters: list[Filter] | None = None):
        return self._client.update_entities(EntityType.PRODUCT, products, filters)

    def create(self, products: list[dict], filters: list[Filter] | None = None):
        return self._client.create_entities(EntityType.PRODUCT, products, filters)

    def replace_existing_file_by_path(
        self,
        product_id: int,
        short_uuid: str,
        path: str,
        metadata: dict | None = None,
        extra: dict | None = None,
    ):
        """
        Adds an image to a product by uploading the image from a specified file path.

        This method reads the image file, determines its MIME type, and uploads it to a
        signed URL obtained from the server. After uploading, it updates the product
        with the new file information. By leveraging the `extra` parameter, you can
        add a wide range of additional fields depending on the file type being set
        (e.g., CAD files, PDFs, or images).

        Args:
            product_id (int): ID of the product to which the file will be associated.
            short_uuid (str): Short UUID extracted from the existing blob ID.
            image_path (str): File path of the asset (image, CAD, PDF) to be uploaded.
            usage (str | None): DEPRECATED. Usage string (e.g., "pro-g"). Default: None.
            metadata (dict | None): Optional metadata associated with the asset.
            extra (dict | None): An optional dictionary of additional fields to include
            in the uploaded file object. The structure and allowed fields depend on
            the file type.

            Possible keys include, but are not limited to, the following structures:

            Extra Args For CAD Files:
                {
                    "file_type": "cad",
                    "file_name_original": str,
                    "description": str,
                    "title": str,
                    "release_datetime": str (ISO 8601 datetime),
                    "direct_link": {
                        "url": str,
                        "is_enabled": bool
                    }
                }

            Extra Args For PDF File:
                {
                    "file_name_original": str,
                    "description": str,
                    "title": str,
                    "release_datetime": str (ISO 8601 datetime),
                    "direct_link": {
                        "url": str,
                        "is_enabled": bool
                    },
                    "pdf_type": str (e.g., "manual"),
                    "page_count": int,
                    "languages": [str, ...],
                    "preview_image": {
                        "description": str,
                        "direct_link": {
                            "url": str,
                            "is_enabled": bool
                        }
                    }
                }

            Extra Args For images:
                {
                    "description": str,
                    "list_order": int,
                    "image_usages": list[str] (e.g., ["pro-sq"]),
                    "direct_link": {
                        "url": str,
                        "is_enabled": bool
                }

        Raises:
            Exception: If the content type of the image cannot be determined, if the
                signed URL request fails, or if the product cannot be retrieved/updated.

        Returns:
            dict: The updated product information after adding the file.

        Example:
            ```python
            # Define product ID and image path
            product_id = 12345
            short_uuid = "123e4567" # short uuid extracted from the existing blob id
            image_path = "/path/to/image.jpg"

            # Add image to product with some extra parameters
            extra_params = {
                "file_name_original": "image.jpg",
                "description": "A sample image",
                "title": "Sample Title"
            }

            updated_product = client.products.replace_existing_file_by_path(
                product_id, short_uuid, image_path, extra=extra_params
            )

            # Print updated product information
            print(updated_product)
            ```
        """
        raise NotImplementedError
        file_data, mime_type = get_file_data_and_mimetype(path)
        asset_type = get_asset_type_from_mime_type(mime_type)
        if not asset_type:
            raise Exception(
                f"Could not determine asset type from the following: {mime_type}"
            )
        endpoint = get_entity_asset_type_endpoint(
            EntityType.PRODUCT, product_id, asset_type
        )
        if not endpoint:
            raise Exception(f"Could not determine url for product & asset {asset_type}")
        blob_id = self._client.upload_file(
            file_data, mime_type, endpoint, metadata, short_uuid
        )
        product = self._client.get_entity(EntityType.PRODUCT, product_id)
        if product.status != 200:
            raise Exception(f"Failed to get product: {product.data}")
        extra = extra or {}
        new_image = gen_new_file_object(blob_id, **extra)
        product = add_image_to_product(product.json(), new_image)  # type: ignore
        return self._client.update_entities(EntityType.PRODUCT, [product])

    def add_image_by_path(
        self,
        product_id: int,
        image_path: str,
        usage: str = "pro-g",
        metadata: dict | None = None,
    ):
        """
        Adds an image to a product by uploading the image from a specified file path.

        This method reads the image file, determines its MIME type, and uploads it to a
        signed URL obtained from the server. After uploading, it updates the product
        with the new image information.

        Args:
            product_id (int): The ID of the product to which the image will be added.
            image_path (str): The file path of the image to be uploaded.
            usage (str | None): DEPRECATED e.g. "pro-g", "pro-g". Defaults to "pro-g".
            metadata (dict | None): Optional metadata to be associated with the image.

        Raises:
            Exception: If the content type of the image cannot be determined or if the
            signed URL request fails.

        Returns:
            dict: The updated product information after adding the image.

        Example:
            ```python
            # Define product ID and image path
            product_id = 12345
            image_path = "/path/to/image.jpg"

            # Add image to product
            updated_product = client.products.add_image_by_path(product_id, image_path)

            # Print updated product information
            print(updated_product)
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
        request = {"expiration": 900, "mime_type": f"{content_type}"}
        if metadata:
            request["headers"] = metadata
        product_signed_url = PRODUCT_SIGNED_URL_ENDPOINT.format(product_id=product_id)
        signed_url_endpoint = f"{self._client._base_url}{product_signed_url}"
        signed_url_response = self._client._do_request(
            "POST", signed_url_endpoint, json=request
        )
        response_data = json.loads(signed_url_response.data.decode("utf-8"))
        if "signed_url" not in response_data:
            raise Exception(f"Failed to get signed url: {response_data}")
        headers = {"Content-Type": content_type}
        if metadata:
            headers.update(metadata)
        resp = http.request(
            "PUT", response_data["signed_url"], body=image_data, headers=headers
        )
        if resp.status != 200:
            raise Exception(
                f"Failed to upload image. Status code: {resp.status}. {resp.data}"
            )
        if "x-goog-generation" not in resp.headers:
            raise Exception("Missing 'x-goog-generation' header in the response")
        generation = resp.headers["x-goog-generation"]
        blob_id = response_data["blob_name"] + "/" + str(generation)
        product = self._client.get_entity(EntityType.PRODUCT, product_id)
        if product.status != 200:
            raise Exception(f"Failed to get product: {product.data}")
        new_image = gen_new_image_object(blob_id, usage)
        product = add_image_to_product(product.json(), new_image)  # type: ignore
        return self._client.update_entities(EntityType.PRODUCT, [product])


class CreatorsResource(BaseResource):
    def get(
        self, filters: list[Filter] | None = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Retrieves creators with optional filtering, returning them as a generator
        that yields each creator one at a time.

        Available filters:
            - creator_ids (str): Filter by comma separated creator IDs.

        Note that the following filters are automatically added to the query:
            - skip (int): Number of records to skip.
            - limit (int): Maximum number of records to retrieve.

        Args:
            filters (list[Filter] | None): A list of filters to apply to the query.

        Yields:
            dict: A dictionary representing a single creator.

        Example:
            ```python
            # Define filters
            filters = [Filter("creator_ids", "12345, 78910")]

            # Get creators (pagination handled internally)
            creators = client.creators.get(filters=filters)

            # Iterate over the results without worrying about pagination
            for c in creators:
                print(f"ID: {c['creator_id']}, Name: {c['name']}")
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
            response = self._client.get_entities(EntityType.CREATOR, filters)
            if response.status != 200:
                break
            for item in response.json():  # type: ignore
                yield item
            skip = int(skip_filter.value) + int(limit_filter.value)
            skip_filter.value = str(skip)
            filters = [f for f in filters if f.name != "skip"]
            filters.append(skip_filter)

    def get_by_id(self, creator_id: int):
        return self._client.get_entity(EntityType.CREATOR, creator_id)

    def update(self, creators: list[dict], filters: list[Filter] | None = None):
        return self._client.update_entities(EntityType.CREATOR, creators, filters)

    def create(self, creators: list[dict], filters: list[Filter] | None = None):
        return self._client.create_entities(EntityType.CREATOR, creators, filters)


class FamiliesResource(BaseResource):
    def get(
        self, filters: list[Filter] | None = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Retrieves families with optional filtering, returning them as a generator
        that yields each family one at a time.

        Available filters:
            - family_ids (str): Filter by comma separated family IDs.

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


class FiltersResource(BaseResource):
    def get(
        self, filters: list[Filter] | None = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Retrieves filters with optional filtering, returning them as a generator
        that yields each filter one at a time.

        Available filters:
            - filter_ids (str): Filter by comma separated filter IDs.

        Note that the following filters are automatically added to the query:
            - skip (int): Number of records to skip.
            - limit (int): Maximum number of records to retrieve.

        Args:
            filters (list[Filter] | None): A list of filters to apply to the query.

        Yields:
            dict: A dictionary representing a single filter.

        Example:
            ```python
            # Define filters
            filters = [Filter("filter_ids", "12345, 78910")]

            # Get filters (pagination handled internally)
            filters = client.filters.get(filters=filters)

            # Iterate over the results without worrying about pagination
            for f in filters:
                print(f"ID: {f['filter_id']}, Name: {f['name_en']}")
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
            response = self._client.get_entities(EntityType.FILTER, filters)
            if response.status != 200:
                break
            for item in response.json():  # type: ignore
                yield item
            skip = int(skip_filter.value) + int(limit_filter.value)
            skip_filter.value = str(skip)
            filters = [f for f in filters if f.name != "skip"]
            filters.append(skip_filter)

    def get_by_id(self, filter_id: int):
        return self._client.get_entity(EntityType.FILTER, filter_id)

    def update(
        self, filters_data: list[dict], query_filters: list[Filter] | None = None
    ):
        return self._client.update_entities(
            EntityType.FILTER, filters_data, query_filters
        )

    def create(
        self, filters_data: list[dict], query_filters: list[Filter] | None = None
    ):
        return self._client.create_entities(
            EntityType.FILTER, filters_data, query_filters
        )


class StoriesResource(BaseResource):
    def get(
        self, filters: list[Filter] | None = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Retrieves stories with optional filtering, returning them as a generator
        that yields each story one at a time.

        Available filters:
            - story_ids (str): Filter by comma separated story IDs.

        Note that the following filters are automatically added to the query:
            - skip (int): Number of records to skip.
            - limit (int): Maximum number of records to retrieve.

        Args:
            filters (list[Filter] | None): A list of filters to apply to the query.

        Yields:
            dict: A dictionary representing a single story.

        Example:
            ```python
            # Define filters
            filters = [Filter("story_ids", "12345, 78910")]

            # Get stories (pagination handled internally)
            stories = client.stories.get(filters=filters)

            # Iterate over the results without worrying about pagination
            for s in stories:
                print(f"ID: {s['story_id']}, Name: {s['name']}")
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
            response = self._client.get_entities(EntityType.STORY, filters)
            if response.status != 200:
                break
            for item in response.json():  # type: ignore
                yield item
            skip = int(skip_filter.value) + int(limit_filter.value)
            skip_filter.value = str(skip)
            filters = [f for f in filters if f.name != "skip"]
            filters.append(skip_filter)

    def get_by_id(self, story_id: int):
        return self._client.get_entity(EntityType.STORY, story_id)

    def update(self, stories: list[dict], filters: list[Filter] | None = None):
        return self._client.update_entities(EntityType.STORY, stories, filters)

    def create(self, stories: list[dict], filters: list[Filter] | None = None):
        return self._client.create_entities(EntityType.STORY, stories, filters)


class SpacesResource(BaseResource):
    def get(
        self, filters: list[Filter] | None = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Retrieves spaces with optional filtering, returning them as a generator
        that yields each space one at a time.

        Available filters:
            - space_ids (str): Filter by comma separated space IDs.

        Note that the following filters are automatically added to the query:
            - skip (int): Number of records to skip.
            - limit (int): Maximum number of records to retrieve.

        Args:
            filters (list[Filter] | None): A list of filters to apply to the query.

        Yields:
            dict: A dictionary representing a single space.

        Example:
            ```python
            # Define filters
            filters = [Filter("space_ids", "12345, 78910")]

            # Get spaces (pagination handled internally)
            spaces = client.spaces.get(filters=filters)

            # Iterate over the results without worrying about pagination
            for s in spaces:
                print(f"ID: {s['space_id']}, Space Type: {s['space_type']}")
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
            response = self._client.get_entities(EntityType.SPACE, filters)
            if response.status != 200:
                break
            for item in response.json():  # type: ignore
                yield item
            skip = int(skip_filter.value) + int(limit_filter.value)
            skip_filter.value = str(skip)
            filters = [f for f in filters if f.name != "skip"]
            filters.append(skip_filter)

    def get_by_id(self, space_id: int):
        return self._client.get_entity(EntityType.SPACE, space_id)

    def update(self, spaces: list[dict], filters: list[Filter] | None = None):
        return self._client.update_entities(EntityType.SPACE, spaces, filters)

    def create(self, spaces: list[dict], filters: list[Filter] | None = None):
        return self._client.create_entities(EntityType.SPACE, spaces, filters)


class GroupsResource(BaseResource):
    def get(
        self, filters: list[Filter] | None = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Retrieves groups with optional filtering, returning them as a generator
        that yields each group one at a time.

        Available filters:
            - group_ids (str): Filter by comma separated group IDs.

        Note that the following filters are automatically added to the query:
            - skip (int): Number of records to skip.
            - limit (int): Maximum number of records to retrieve.

        Args:
            filters (list[Filter] | None): A list of filters to apply to the query.

        Yields:
            dict: A dictionary representing a single space.

        Example:
            ```python
            # Define filters
            filters = [Filter("group_ids", "12345, 78910")]

            # Get groups (pagination handled internally)
            groups = client.groups.get(filters=filters)

            # Iterate over the results without worrying about pagination
            for g in groups:
                print(f"ID: {g['group_id']}, Name: {g['name_en']}")
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
            response = self._client.get_entities(EntityType.GROUP, filters)
            if response.status != 200:
                break
            for item in response.json():  # type: ignore
                yield item
            skip = int(skip_filter.value) + int(limit_filter.value)
            skip_filter.value = str(skip)
            filters = [f for f in filters if f.name != "skip"]
            filters.append(skip_filter)

    def get_by_id(self, group_id: int):
        return self._client.get_entity(EntityType.GROUP, group_id)

    def update(self, groups: list[dict], filters: list[Filter] | None = None):
        return self._client.update_entities(EntityType.GROUP, groups, filters)

    def create(self, groups: list[dict], filters: list[Filter] | None = None):
        return self._client.create_entities(EntityType.GROUP, groups, filters)


class FairsResource(BaseResource):
    def get(
        self, filters: list[Filter] | None = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Retrieves fairs with optional filtering, returning them as a generator
        that yields each fair one at a time.

        Available filters:
            - fair_ids (str): Filter by comma separated fair IDs.

        Note that the following filters are automatically added to the query:
            - skip (int): Number of records to skip.
            - limit (int): Maximum number of records to retrieve.

        Args:
            filters (list[Filter] | None): A list of filters to apply to the query.

        Yields:
            dict: A dictionary representing a single fair.

        Example:
            ```python
            # Define filters
            filters = [Filter("fair_ids", "12345, 78910")]

            # Get fairs (pagination handled internally)
            fairs = client.fairs.get(filters=filters)

            # Iterate over the results without worrying about pagination
            for f in fairs:
                print(f"ID: {f['fair_id']}, Name: {f['name']}")
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
            response = self._client.get_entities(EntityType.FAIR, filters)
            if response.status != 200:
                break
            for item in response.json():  # type: ignore
                yield item
            skip = int(skip_filter.value) + int(limit_filter.value)
            skip_filter.value = str(skip)
            filters = [f for f in filters if f.name != "skip"]
            filters.append(skip_filter)

    def get_by_id(self, fair_id: int):
        return self._client.get_entity(EntityType.FAIR, fair_id)

    def update(self, fairs: list[dict], filters: list[Filter] | None = None):
        return self._client.update_entities(EntityType.FAIR, fairs, filters)

    def create(self, fairs: list[dict], filters: list[Filter] | None = None):
        return self._client.create_entities(EntityType.FAIR, fairs, filters)


class FilesResource(BaseResource):
    def upload_file_to_temp_bucket_by_file_path(
        self, file_path: str, metadata: dict | None = None
    ) -> str:
        """
        Uploads a file to a temporary bucket using the file path.

        Args:
            file_path (str): The path to the file to be uploaded.
            metadata (dict, optional): Additional metadata for the file. Default: None

        Returns:
            str: The blob ID of the uploaded file.

        Example:
            import os
            from daaily.lucy import Client

            # Get the directory of the current file
            script_dir = os.path.dirname(os.path.abspath(__file__))

            # Instantiate the client and overwrite the base URL with staging environment
            client = Client(base_url="https://lucy.staging.daaily.com/api/v2")

            product_id = 1032360

            # Construct the path to the file in the neighboring directory
            file_path = os.path.join(script_dir, "..", "assets", "vitra.jpeg")

            blob_id = client.files.upload_file_to_temp_bucket_by_file_path(file_path)
            print("This is the blob_id of the uploaded asset:", blob_id)
        """
        file_data, mime_type = get_file_data_and_mimetype(file_path)
        asset_type = get_asset_type_from_mime_type(mime_type)
        if not asset_type:
            raise Exception(
                f"Could not determine asset type from the following: {mime_type}"
            )
        file_name = os.path.basename(file_path)
        blob_id = self._client.upload_file(
            file_data, file_name, mime_type, FILE_UPLOADS_UNSPECIFIC_ENDPOINT, metadata
        )
        return blob_id
