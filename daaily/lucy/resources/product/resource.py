import json
import logging
import os
import re
from typing import Any, Dict, Generator
from urllib.parse import urlencode, urlparse

import urllib3

from daaily.lucy.constants import ENTITY_STATUS
from daaily.lucy.enums import AssetType, EntityType, Service
from daaily.lucy.models import Filter
from daaily.lucy.response import Response
from daaily.lucy.utils import (
    add_image_to_product_by_blob_id,
    extract_extension_from_blob_id,
    extract_mime_type_from_extension,
    gen_new_image_object_with_extras,
    get_file_data_and_mimetype,
)

from .. import BaseResource

PRODUCT_SIGNED_URL_ENDPOINT = "/products/{product_id}/images/online"
PRODUCT_IMAGE_UPLOAD_ENDPOINT = "/products/{product_id}/image/upload"
PRODUCT_PDF_UPLOAD_ENDPOINT = "/products/{product_id}/pdf/upload"
PRODUCT_PDF_SIGNED_URL_ENDPOINT = "/products/{product_id}/pdf/signed-url"
PRODUCT_PDF_PREVIEW_SIGNED_URL_ENDPOINT = (
    "/products/{product_id}/pdf/signed-url-preview"
)
PRODUCT_CAD_UPLOAD_ENDPOINT = "/products/{product_id}/cad/upload"
PRODUCT_CAD_SIGNED_URL_ENDPOINT = "/products/{product_id}/cad/signed-url"

http = urllib3.PoolManager()  # for handling HTTP requests without auth

logger = logging.getLogger(__name__)


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
            response = self._client.get_entities(EntityType.PRODUCT, new_filters)
            if response.status != 200:
                break
            for item in response.json():  # type: ignore
                yield item
            skip_value = str(int(skip_value) + int(limit_value))
            skip_filter.value = skip_value
            new_filters = [f for f in new_filters if f.name != "skip"]
            new_filters.append(skip_filter)

    def get_by_id(self, product_id: int):
        return self._client.get_entity(EntityType.PRODUCT, product_id)

    def refresh(self, product_id: int):
        """
        This will refresh the product data. It will not return anything but will
        simply refresh the data which will then update the denormalized data on the
        product. It will not change the revision_uuid.
        """
        return self._client.refresh_entity(EntityType.PRODUCT, product_id)

    def update(
        self,
        products: list[dict],
        filters: list[Filter] | None = None,
        service: Service = Service.SPARKY,
    ):
        return self._client.update_entities(
            EntityType.PRODUCT, products, filters, service
        )

    def update_one(self, product: dict, service: Service = Service.SPARKY):
        return self._client.update_entity(EntityType.PRODUCT, product, service)

    def create(
        self,
        products: list[dict],
        filters: list[Filter] | None = None,
        service: Service = Service.SPARKY,
    ):
        return self._client.create_entities(
            EntityType.PRODUCT, products, filters, service=service
        )

    def upload_image(
        self,
        product_id: int,
        image_path: str | None = None,
        image_bytes: bytes | None = None,
        mime_type: str | None = None,
        filename: str | None = None,
        old_blob_id: str | None = None,
        **kwargs,
    ) -> Any:
        """
        Uploads an image file to a product and returns the blob ID.
        Does not add the image file to the product.

        Args:
            product_id (int): The unique identifier of the product.
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
                    "image_blob_id": "m-on/310089/products/12345/image/file.jpg",
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
            response = client.products.upload_image(
                product_id=12345,
                image_path="/path/to/image_file.jpg"
            )

            # Upload an image file using binary data
            response = client.products.upload_image(
                product_id=12345,
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
        prod_image_upload_url = PRODUCT_IMAGE_UPLOAD_ENDPOINT.format(
            product_id=product_id
        )
        url = f"{self._client._base_url}{prod_image_upload_url}"
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

    def upload_pdf(  # noqa: C901
        self,
        product_id: int,
        pdf_path: str | None = None,
        pdf_bytes: bytes | None = None,
        mime_type: str | None = None,
        pdf_type: str | None = None,
        filename: str | None = None,
        old_blob_id: str | None = None,
        **kwargs,
    ) -> Any:
        """
        Uploads a PDF file to a product and returns the blob ID.
        Does not add the PDF file to the product.

        Args:
            product_id (int): The unique identifier of the product.
            pdf_path (str | None): The local file path to the PDF file.
            pdf_bytes (bytes | None): The binary data of the PDF file.
            mime_type (str | None): The MIME type of the PDF file.
            pdf_type (str | None): The type of the PDF file.
            filename (str | None): The name of the PDF file.
            old_blob_id (str | None): The blob ID of the existing PDF file.
            **kwargs: Additional keyword arguments containing PDF metadata.

        Returns:
            Any: The response data from the server.
            For example:
                {
                    "pdf_blob_id": "m-on/310089/products/12345/pdf/file.pdf",
                    "pdf_mime_type": "application/pdf",
                    "pdf_size": 123456,
                    "pdf_page_count": 3,
                    "preview_image_blob_id": "m-on/310089/products/12345/pdf/image.jpg",
                    "preview_image_size": 1234,
                    "preview_image_mime_type": "image/jpeg",
                    "preview_image_height": 600,
                    "preview_image_width": 200
                }

        Raises:
            Exception: If neither pdf_path nor pdf_bytes is provided.
            Exception: If the content type of the PDF file is not application/pdf.
            Exception: If the upload fails.

        Example:
            ```python
            # Upload a PDF file using a local file
            response = client.products.upload_pdf(
                product_id=12345,
                pdf_path="/path/to/pdf_file.pdf"
            )

            # Upload a PDF file using binary data
            response = client.products.upload_pdf(
                product_id=12345,
                pdf_bytes=b"binary_data",
                mime_type="application/pdf",
                filename="pdf_file.pdf"
            )
            ```
        """
        if not pdf_path and not pdf_bytes:
            raise Exception("Either pdf_path or pdf_bytes must be provided")
        if pdf_path:
            pdf_data, content_type, filename = get_file_data_and_mimetype(pdf_path)
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
            headers = dict(item for item in kwargs.items() if isinstance(item[1], str))
        else:
            headers = {}
        prod_pdf_upload_url = PRODUCT_PDF_UPLOAD_ENDPOINT.format(product_id=product_id)
        url = f"{self._client._base_url}{prod_pdf_upload_url}"
        params = {}
        if old_blob_id:
            old_extension = extract_extension_from_blob_id(old_blob_id)
            old_mime_type = extract_mime_type_from_extension(old_extension)
            if old_mime_type == content_type:
                params["old_blob_id"] = old_blob_id
        if pdf_type:
            params["pdf_type"] = pdf_type
        if params:
            url += "?" + urlencode(params)
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

    def get_pdf_signed_url(
        self,
        product_id: int,
        pdf_title: str | None = None,
        pdf_type: str | None = None,
        old_blob_id: str | None = None,
    ) -> Any:
        """
        Requests a signed URL for uploading a PDF file to GCS.
        This method sends a request to Lydia for a signed URL that can be used to
        upload a PDF file to Google Cloud Storage (GCS). The signed URL is returned
        in the response, along with the blob ID and blob name.
        Args:
            product_id (int): The unique identifier of the product.
            pdf_title (str | None): The title of the PDF file.
            pdf_type (str | None): The type of the PDF file.
            old_blob_id (str | None): The blob ID of the existing PDF file.
                If provided, it will be used to check if the existing PDF can be
                replaced.
        Returns:
            Any: The response from the server containing the signed URL and other
                details.
                For example:
                    {
                        "signed_url": "string",
                        "blob_id": "string",
                        "blob_name": "string"
                    }
        Raises:
            Exception: If the request fails or if the response is not as expected.
        Example:
            ```python
            # Request a signed URL for uploading a PDF
            response = client.products.get_pdf_signed_url(
                product_id=12345,
                pdf_title="Sample PDF",
                old_blob_id="m-on/310089/pdf/file.pdf"
            )
            ```
        """
        prod_pdf_signed_url_pathname = PRODUCT_PDF_SIGNED_URL_ENDPOINT.format(
            product_id=product_id
        )
        url = f"{self._client._base_url}{prod_pdf_signed_url_pathname}"
        params = {}
        if pdf_title:
            params["pdf_title"] = pdf_title
        if pdf_type:
            params["pdf_type"] = pdf_type
        if old_blob_id:
            params["old_blob_id"] = old_blob_id
        if params:
            url += "?" + urlencode(params)
        resp = self._client._do_request("POST", url)
        if resp.status != 200:
            raise Exception(
                f"Failed to get signed URL. Status code: {resp.status}. {resp.data}"
            )
        return json.loads(resp.data.decode("utf-8"))

    def get_pdf_preview_signed_url(
        self,
        product_id: int,
        mime_type: str,
        pdf_type: str | None = None,
        old_blob_id: str | None = None,
    ) -> Any:
        """
        Requests a signed URL for uploading a PDF preview image to GCS.
        This method sends a request to Lydia for a signed URL that can be used to
        upload a PDF preview image to Google Cloud Storage (GCS). The signed URL is
        returned in the response, along with the blob ID and blob name.
        Args:
            product_id (int): The unique identifier of the product.
            mime_type (str): The MIME type of the preview image.
            pdf_type (str | None): The type of the PDF file.
            old_blob_id (str | None): The blob ID of the existing preview image.
                If provided, it will be used to check if the existing image can be
                replaced.
        Returns:
            Any: The response from the server containing the signed URL and other
                details.
                For example:
                    {
                        "signed_url": "string",
                        "blob_id": "string",
                        "blob_name": "string"
                    }
        Raises:
            Exception: If the request fails or if the response is not as expected.
        Example:
            ```python
            # Request a signed URL for uploading a PDF preview image
            response = client.products.get_pdf_preview_signed_url(
                product_id=12345,
                mime_type="image/jpeg",
                old_blob_id="m-on/310089/pdf/image.jpg"
            )
            ```
        """
        prod_pdf_preview_signed_url_pathname = (
            PRODUCT_PDF_PREVIEW_SIGNED_URL_ENDPOINT.format(product_id=product_id)
        )
        url = f"{self._client._base_url}{prod_pdf_preview_signed_url_pathname}"
        params = {}
        if old_blob_id:
            params["old_blob_id"] = old_blob_id
        if mime_type:
            params["mime_type"] = mime_type
        if pdf_type:
            params["pdf_type"] = pdf_type
        if params:
            url += "?" + urlencode(params)
        resp = self._client._do_request("POST", url)
        if resp.status != 200:
            raise Exception(
                f"Failed to get signed URL. Status code: {resp.status}. {resp.data}"
            )
        return json.loads(resp.data.decode("utf-8"))

    def upload_cad(  # noqa: C901
        self,
        product_id: int,
        cad_path: str | None = None,
        cad_bytes: bytes | None = None,
        mime_type: str | None = None,
        filename: str | None = None,
        old_blob_id: str | None = None,
        **kwargs,
    ) -> Any:
        """
        Uploads a CAD file to a product and returns the blob ID.
        Does not add the CAD file to the product.

        Args:
            product_id (int): The unique identifier of the product.
            cad_path (str | None): The local file path to the CAD file.
            cad_bytes (bytes | None): The binary data of the CAD file.
            mime_type (str | None): The MIME type of the CAD file.
            filename (str | None): The name of the CAD file.
            old_blob_id (str | None): The blob ID of the existing CAD file.
            **kwargs: Additional keyword arguments containing CAD metadata.

        Returns:
            Any: The response data from the server.
            For example:
                {
                    "cad_blob_id": "m-on/3100089/products/123456/cad/some-cad-file",
                    "cad_mime_type": "application/...",
                    "cad_file_extension": "dwg",
                    "cad_file_name_original": "string",
                    "cad_size": 123456,
                }

        Raises:
            Exception: If neither cad_path nor cad_bytes is provided.
            Exception: If the content type of the CAD file is not application/ or image/
            Exception: If the upload fails.

        Example:
            ```python
            # Upload a CAD file using a local file
            response = client.products.upload_cad(
                product_id=12345,
                cad_path="/path/to/cad_file.dwg",
                filename="cad_file.dwg"
            )

            # Upload a CAD file using binary data
            response = client.products.upload_cad(
                product_id=12345,
                cad_bytes=b"binary_data",
                mime_type="application/dwg",
                filename="cad_file.dwg"
            )
            ```
        """
        if not cad_path and not cad_bytes:
            raise Exception("Either cad_path or cad_bytes must be provided")
        if cad_path:
            cad_data, content_type, filename = get_file_data_and_mimetype(cad_path)
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
            headers = dict(item for item in kwargs.items() if isinstance(item[1], str))
        else:
            headers = {}
        prod_cad_upload_url = PRODUCT_CAD_UPLOAD_ENDPOINT.format(product_id=product_id)
        url = f"{self._client._base_url}{prod_cad_upload_url}"
        params = {}
        if old_blob_id:
            old_extension = extract_extension_from_blob_id(old_blob_id)
            old_mime_type = extract_mime_type_from_extension(old_extension)
            if old_mime_type == content_type:
                params["old_blob_id"] = old_blob_id
        if params:
            url += "?" + urlencode(params)
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

    def get_cad_signed_url(
        self,
        product_id: int,
        file_extension: str,
        cad_title: str | None = None,
        old_blob_id: str | None = None,
    ) -> Any:
        """
        Requests a signed URL for uploading a CAD file to GCS.

        This method sends a request to Lydia for a signed URL that can be used to
        upload a CAD file to Google Cloud Storage (GCS). The signed URL is returned
        in the response, along with the blob ID and blob name.

        Args:
            product_id (int): The unique identifier of the product.
            file_extension (str): The file extension of the CAD file.
            cad_title (str | None): The title of the CAD file.
            old_blob_id (str | None): The blob ID of the existing CAD file.
                If provided, it will be used to check if the existing CAD can be
                replaced.
        Returns:
            Any: The response from the server containing the signed URL and other
                details.
                For example:
                    {
                        "signed_url": "string",
                        "blob_id": "string",
                        "blob_name": "string"
                    }
        Raises:
            Exception: If the request fails or if the response is not as expected.
        Example:
            ```python
            # Request a signed URL for uploading a CAD file
            response = client.products.get_cad_signed_url(
                product_id=12345,
                file_extension="dwg",
                cad_title="Sample CAD",
                old_blob_id="m-on/310089/cad/file.dwg"
            )
            ```
        """
        prod_pdf_signed_url_pathname = PRODUCT_CAD_SIGNED_URL_ENDPOINT.format(
            product_id=product_id
        )
        url = f"{self._client._base_url}{prod_pdf_signed_url_pathname}"
        params = {}
        params["file_extension"] = file_extension
        if cad_title:
            params["cad_title"] = cad_title
        if old_blob_id:
            params["old_blob_id"] = old_blob_id
        if params:
            url += "?" + urlencode(params)
        resp = self._client._do_request("POST", url)
        if resp.status != 200:
            raise Exception(
                f"Failed to get signed URL. Status code: {resp.status}. {resp.data}"
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

    def deter_score_up_to_date(self, product_id: int) -> bool:
        """
        Determine if the product score is still up to date. That means that
        the fields used to calculate the score have not been changed since the last
        product score update.

        Args:
            product_id (int): The unique identifier of the product to inspect.
            scored_fields (list[str]): A list of field names the score is based on.

        Returns:
            boolean: True if the score is up to date, False otherwise.
        """
        product = self._client.get_entity(EntityType.PRODUCT, product_id)
        product_data = product.json()
        if not product_data:
            raise Exception("Could not deserialize product")
        scored_fields = product_data.get("product_score", {}).get("scored_fields")
        score_last_updated_at = product_data.get("product_score", {}).get("updated_at")
        if not scored_fields or not score_last_updated_at:
            raise Exception("Could not find scored fields in product score data")
        filters_score_fields = [
            Filter("limit", "1"),
            Filter("changed_fields", ",".join(scored_fields)),
            Filter("changed_from", score_last_updated_at),
        ]
        audits_response = self._client.get_entity_audits(
            EntityType.PRODUCT, product_id, filters_score_fields
        )
        if audits_response.status == 404:
            return True
        return False

    def add_or_update_image(  # noqa: C901
        self,
        product_id: int,
        image_path: str | None = None,
        image_url: str | None = None,
        old_blob_id: str | None = None,
        **kwargs,
    ) -> Response:
        """
        Adds or updates a product image.

        This function handles the addition or update of a product image. When updating
        an image, an old blob ID must be provided. When creating a new image, either an
        image_path or an image_url must be provided. To replace the image file, both
        an image_path (or image_url) and the old blob ID must be provided. Only one of
        image_path or image_url should be supplied.

        The image can be provided in one of two ways:
            - As a local file using 'image_path'
            - As a remote file using 'image_url'

        The following keys may be included in the kwargs dictionary:

            - blob_id (str): The blob ID of the image.
            - image_usages (list[str] | None): List of image usages, e.g., "pro-g",
                "pro-b".
            - image_type (str | None): The type of image, e.g., "Cut-out image",
                "Ambient image", "Drawing image", "Material image", "Detail image".
            - list_order (int | None): The display order of the image.
            - direct_link (dict | None): Dictionary containing the direct link to the
                image.
            - description (str | None): Description of the image.
            - color (dict | None): Dictionary containing the color details of the image.

        Args:
            product_id (int): The unique identifier of the product.
            image_path (str | None): The local file path to the new image. Required when
                creating a new image or replacing an existing image using a local file.
            image_url (str | None): The URL of the new image. Required when creating a
                new image or replacing an existing image using a remote image source.
            old_blob_id (str | None): The blob ID of the existing image. Required when
                updating an image.
            **kwargs: Additional keyword arguments containing image metadata.

        Raises:
            ValueError: If both image_path and image_url are provided.
            Exception: If neither image_path nor image_url is provided when required,
                or if the old blob ID is missing when updating an image.
            Exception: If the product retrieval fails.
            Exception: If the product deserialization fails.
            Exception: If the old blob ID does not match the blob ID in the image object
            Exception: If the image download (from image_url) or upload fails.
            ValueError: If the image object does not contain a blob_id.

        Returns:
            Any: The updated product object.

        Example:
            ```python
            # Define image details
            image_data = {
                "image_usages": ["pro-b"],
                "image_type": "Cut-out image",
                "list_order": 1,
                "direct_link": {"url": "https://example.com/image.jpg"},
                "description": "A sample product image",
            }

            # Add a new product image using a local file
            response = client.products.add_or_update_image(
                product_id=12345,
                image_path="/path/to/image.jpg",
                **image_data
            )

            # Add a new product image using a URL
            response = client.products.add_or_update_image(
                product_id=12345,
                image_url="https://example.com/image.jpg",
                **image_data
            )

            # Update an existing product image (without replacing the image file)
            response = client.products.add_or_update_image(
                product_id=12345,
                old_blob_id="existing-blob-id",
                **image_data
            )

            # Replace an existing product image with a new one using a local file
            response = client.products.add_or_update_image(
                product_id=12345,
                image_path="/path/to/new_image.jpg",
                old_blob_id="existing-blob-id",
                **image_data
            )

            # Replace an existing product image with a new one using a URL
            response = client.products.add_or_update_image(
                product_id=12345,
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
        response = self._client.get_entity(EntityType.PRODUCT, product_id)
        if response.status != 200:
            raise Exception(
                f"Failed to retrieve product. Status code: {response.status}. "
                + f"{response.data}"
            )
        product = response.json()
        if not product:
            raise Exception("Could not deserialize product")
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
                product_id=product_id,
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
        product = add_image_to_product_by_blob_id(
            product, image, old_blob_id=old_blob_id
        )
        return self._client.update_entity(EntityType.PRODUCT, product)

    def change_image_status(
        self, product_id: int, blob_id: str, target_status: ENTITY_STATUS
    ) -> Response:
        """
        Changes the status of an image associated with a product.

        This function updates the status of a specified image (identified by its blob
        ID) for a given product. The status can be set to "online", "preview", or
        "deleted".

        Args:
            product_id (int): The unique identifier of the product.
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
            response = client.products.change_image_status(
                product_id=12345,
                blob_id="m-on/310089/products/12345/image/file.jpg",
                target_status="deleted"
            )
            ```
        """
        return self._client.move_asset(
            EntityType.PRODUCT, product_id, AssetType.IMAGE, blob_id, target_status
        )

    def change_pdf_status(
        self, product_id: int, blob_id: str, target_status: ENTITY_STATUS
    ) -> Response:
        """
        Changes the status of a PDF associated with a product.

        This function updates the status of a specified PDF (identified by its blob ID)
        for a given product. The status can be set to "online", "preview", or "deleted".

        Args:
            product_id (int): The unique identifier of the product.
            blob_id (str): The blob ID of the PDF whose status is to be changed.
            target_status (Literal["online", "preview", "deleted"]): The target status
                for the PDF.

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
            # Change the status of a PDF to "online"
            response = client.products.change_pdf_status(
                product_id=12345,
                blob_id="m-on/310089/products/12345/pdf/file.pdf",
                target_status="deleted"
            )
            ```
        """
        return self._client.move_asset(
            EntityType.PRODUCT, product_id, AssetType.PDF, blob_id, target_status
        )

    def change_cad_status(
        self, product_id: int, blob_id: str, target_status: ENTITY_STATUS
    ) -> Response:
        """
        Changes the status of a CAD file associated with a product.

        This function updates the status of a specified CAD file (identified by its
        blob ID) for a given product. The status can be set to "online", "preview",
        or "deleted".

        Args:
            product_id (int): The unique identifier of the product.
            blob_id (str): The blob ID of the CAD file whose status is to be changed.
            target_status (Literal["online", "preview", "deleted"]): The target status
                for the CAD file.

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
            # Change the status of a CAD file to "online"
            response = client.products.change_cad_status(
                product_id=12345,
                blob_id="m-on/310089/products/12345/cad/file.dwg",
                target_status="deleted"
            )
            ```
        """
        return self._client.move_asset(
            EntityType.PRODUCT, product_id, AssetType.CAD, blob_id, target_status
        )

    def add_or_update_attributes(  # noqa: C901
        self,
        product_id: int,
        attributes: list[dict[str, Any]],
        service: Service = Service.SPARKY,
        overwrite_existing: bool = False,
        dry_run: bool = False,
    ) -> dict | None:
        """
        Adds attributes to a product.

        attributes is a list of tuples, where each tuple contains the attribute
        name english, the value and the attribute type. The attribute type must
        be one of the values in the AttributeType enum.


        Returns the updated product object.

        Args:
            product_id (int): The unique identifier of the product.
            attributes (list[dict[str, Any]]): A list of dictionaries containing
                attribute details. Each dictionary should contain the following keys:
                - name (str): The name of the attribute.
                - value (Any): The value of the attribute.
            service (Service): The service to use for the operation. Default is sparky.
            overwrite_existing (bool): If True, existing attributes will be overwritten.
                Default is False. Though it will only overwrite the attributes that
                were set by the same source actor. Like a user associated attribute
                will not be overwritten by an AI attribute.
            dry_run (bool): If True, the operation will not be executed, and the
                updated product object will be returned without making any changes.
        """
        product = self.get_by_id(product_id).json()
        if not product:
            raise Exception(f"Product with ID {product_id} not found")
        product["attributes"] = product.get("attributes") or []
        if overwrite_existing:
            source_actor = None
            for attribute in attributes:
                if not source_actor:
                    source_actor = attribute.get("source_actor", "internal_user")
                elif source_actor != attribute.get("source_actor", "internal_user"):
                    raise ValueError(
                        "All attributes must have the same source actor when "
                        + "overwrite_existing is True"
                    )
                attribute["source_actor"] = source_actor
                source_type = attribute.get("source_type", "unknown")
                attribute["source_type"] = source_type
            # remove all attributes that were set by the same source actor
            product["attributes"] = [
                attr
                for attr in product["attributes"]
                if attr.get("source_actor") != source_actor
            ]
        for attribute in attributes:
            source_actor = attribute.get("source_actor")
            for product_attribute in product["attributes"]:
                if (
                    product_attribute["name"] == attribute["name"]
                    and product_attribute["source_actor"] == source_actor
                ):
                    product_attribute["value"] = attribute["value"]
                    source_type = product_attribute.get("source_type", "unknown")
                    product_attribute["source_type"] = source_type
                    break
            else:
                product["attributes"].append(attribute)
        if dry_run:
            return product
        update_resp = self.update_one(product, service=service)
        if update_resp.status != 200:
            raise Exception(
                f"Failed to update product {product_id}. Status: {update_resp.status}"
            )
        return update_resp.json()
