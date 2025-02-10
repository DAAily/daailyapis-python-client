import json
from typing import Any, Dict, Generator

import urllib3

from daaily.lucy.enums import EntityType
from daaily.lucy.models import Filter
from daaily.lucy.utils import get_file_data_and_mimetype

from . import BaseResource

PRODUCT_SIGNED_URL_ENDPOINT = "/products/{product_id}/images/online"
PRODUCT_IMAGE_UPLOAD_ENDPOINT = "/products/{product_id}/image/upload"
PRODUCT_PDF_UPLOAD_ENDPOINT = "/products/{product_id}/pdf/upload"
PRODUCT_CAD_UPLOAD_ENDPOINT = "/products/{product_id}/cad/upload"

http = urllib3.PoolManager()  # for handling HTTP requests without auth


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

    def upload_image(
        self,
        product_id: int,
        filename: str,
        image_path: str | None = None,
        image_bytes: bytes | None = None,
        mime_type: str | None = None,
        **kwargs,
    ) -> Any:
        """ """
        if not image_path and not image_bytes:
            raise Exception("Either image_path or image_bytes must be provided")
        if image_path:
            image_data, content_type = get_file_data_and_mimetype(image_path)
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
            headers = dict(kwargs.items())
        else:
            headers = {}
        prod_image_upload_url = PRODUCT_IMAGE_UPLOAD_ENDPOINT.format(
            product_id=product_id
        )
        url = f"{self._client._base_url}{prod_image_upload_url}"
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

    def upload_pdf(
        self,
        product_id: int,
        filename: str,
        pdf_path: str | None = None,
        pdf_bytes: bytes | None = None,
        mime_type: str | None = None,
        **kwargs,
    ) -> Any:
        """ """
        if not pdf_path and not pdf_bytes:
            raise Exception("Either pdf_path or pdf_bytes must be provided")
        if pdf_path:
            pdf_data, content_type = get_file_data_and_mimetype(pdf_path)
        else:
            if not mime_type:
                raise ValueError(
                    "If 'pdf_bytes' is provided, 'mime_type' must be specified."
                )
            pdf_data = pdf_bytes
            content_type = mime_type
        if content_type is None:
            raise Exception("Could not determine content type for pdf")
        if content_type != "application/pdf":
            raise Exception(f"File is not pdf type. Detected: {content_type}")
        if kwargs:
            headers = dict(kwargs.items())
        else:
            headers = {}
        prod_pdf_upload_url = PRODUCT_PDF_UPLOAD_ENDPOINT.format(product_id=product_id)
        url = f"{self._client._base_url}{prod_pdf_upload_url}"
        resp = self._client._do_request(
            "POST",
            url,
            fields={"file": (filename, pdf_data, content_type)},
            headers=headers,
        )
        if resp.status != 200:
            raise Exception(
                f"Failed to upload pdf. Status code: {resp.status}. {resp.data}"
            )
        return json.loads(resp.data.decode("utf-8"))

    def upload_cad(
        self,
        product_id: int,
        filename: str,
        cad_path: str | None = None,
        cad_bytes: bytes | None = None,
        mime_type: str | None = None,
        **kwargs,
    ) -> Any:
        """ """
        if not cad_path and not cad_bytes:
            raise Exception("Either cad_path or cad_bytes must be provided")
        if cad_path:
            cad_data, content_type = get_file_data_and_mimetype(cad_path)
        else:
            if not mime_type:
                raise ValueError(
                    "If 'cad_bytes' is provided, 'mime_type' must be specified."
                )
            cad_data = cad_bytes
            content_type = mime_type
        if content_type is None:
            raise Exception("Could not determine content type for cad")
        if not content_type.startswith("application/") and not content_type.startswith(
            "image/"
        ):
            raise Exception(f"File is not cad type. Detected: {content_type}")
        if kwargs:
            headers = dict(kwargs.items())
        else:
            headers = {}
        prod_cad_upload_url = PRODUCT_CAD_UPLOAD_ENDPOINT.format(product_id=product_id)
        url = f"{self._client._base_url}{prod_cad_upload_url}"
        resp = self._client._do_request(
            "POST",
            url,
            fields={"file": (filename, cad_data, content_type)},
            headers=headers,
        )
        if resp.status != 200:
            raise Exception(
                f"Failed to upload cad. Status code: {resp.status}. {resp.data}"
            )
        return json.loads(resp.data.decode("utf-8"))

    def deter_ownership_of_fields(
        self, product_id: int, changed_fields: list[str], owner_email: str
    ) -> dict | None:
        """
        Determine the ownership of specific fields within a product.

        This function checks whether a given user (identified by their email)
        is considered the owner of one or more product fields. Ownership is
        established by verifying if the user was the last one to modify a field.
        For example, if a user wants to know whether they currently "own" the
        "name" field, this function will retrieve the change history for that
        field and confirm ownership if the user was the last modifier.

        Special cases:
        - If no changes have been made to the product and the provided email
            matches the product creator's email, the function returns all fields
            specified in the changed_fields parameter.
        - If no changes have been made and the email does not match the creator,
            the function returns None.

        Note:
        Regardless of the case, the returned data should be treated as a subset
        of the full product object. It may contain only the relevant fields and
        metadata rather than the complete product details.

        Args:
            product_id (int): The unique identifier of the product to inspect.
            changed_fields (list[str]): A list of field names to evaluate for ownership.
            owner_email (str): The email of the user whose ownership is to be verified.


        Returns:
            dict or None: A dict containing ownership details for each specified field.
            For example, the output might look like:

                {
                    "cads": [
                        {
                            "blob_id": "m-on/3100089/products/123456/cad/some-cad-file",
                            "file_type": "application/...",
                            "file_name_original": "some-cad-file",
                            "description": "Some CAD file",
                            ...
                        }
                    ],
                    "name_en": "John Doe",
                    "live_link": {
                        "url": "https://www.some-url.com",
                        "is_enabled": True,
                        ...
                    }
                }

            If no modifications have been made and the provided email does not match
            the product creator, None is returned.
        """
        ownership_results = {}
        for field in changed_fields:
            filters = [
                Filter("limit", "100"),
                Filter("skip", "0"),
                Filter("changed_fields", field),
            ]
            audits_response = self._client.get_entity_audits(
                EntityType.PRODUCT, product_id, filters
            )
            audits = audits_response.json()
            # Assuming the result set is sorted by "updated_at" in descending order
            for audit in audits or []:
                if field not in audit["changes"]:
                    continue
                if audit.get("changed_by") != owner_email:
                    # This means the first item in the list is not owned by the user
                    # and so the last to change was not the user.
                    break
                new_value = audit["changes"][field]["new_value"]
                if isinstance(new_value, list):
                    old_value = audit["changes"][field]["old_value"]
                    # We assume that a dict present in new_value that does not match
                    # any dict in old_value should be considered as "changed"
                    # or "newly owned".
                    changed_items = [
                        new_item
                        for new_item in new_value
                        if not any(new_item == old_item for old_item in old_value)
                    ]
                    ownership_results[field] = changed_items
                else:
                    ownership_results[field] = new_value
                # Once we have found an audit for this field where the owner is the
                # updater, we don't need to look further.
                break
        # case when there are no applicable changes and the product was created by owner
        if not ownership_results:
            product = self._client.get_entity(EntityType.PRODUCT, product_id)
            if product.status == 200:
                product_data = product.json()
                if product_data and product_data["created_by"] == owner_email:
                    for field in changed_fields:
                        ownership_results[field] = product_data.get(field)
        return ownership_results or None
