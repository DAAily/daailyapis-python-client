import json
from typing import Any, Dict, Generator
from urllib.parse import urlencode

from daaily.lucy.enums import EntityType, Service
from daaily.lucy.models import Filter
from daaily.lucy.utils import (
    extract_extension_from_blob_id,
    extract_mime_type_from_extension,
    get_file_data_and_mimetype,
)

from .. import BaseResource

DISTRIBUTOR_PDF_UPLOAD_ENDPOINT = "/distributors/{distributor_id}/pdf/upload"
DISTRIBUTOR_PDF_SIGNED_URL_ENDPOINT = "/distributors/{distributor_id}/pdf/signed-url"
DISTRIBUTOR_PDF_PREVIEW_SIGNED_URL_ENDPOINT = (
    "/distributors/{distributor_id}/pdf/signed-url-preview"
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
            response = self._client.get_entities(EntityType.DISTRIBUTOR, new_filters)
            if response.status != 200:
                break
            for item in response.json():  # type: ignore
                yield item
            skip_value = str(int(skip_value) + int(limit_value))
            skip_filter.value = skip_value
            new_filters = [f for f in new_filters if f.name != "skip"]
            new_filters.append(skip_filter)

    def get_by_id(self, distributor_id: int):
        return self._client.get_entity(EntityType.DISTRIBUTOR, distributor_id)

    def update(
        self,
        distributors: list[dict],
        filters: list[Filter] | None = None,
        service: Service = Service.SPARKY,
    ):
        return self._client.update_entities(
            EntityType.DISTRIBUTOR, distributors, filters, service=service
        )

    def create(
        self,
        distributors: list[dict],
        filters: list[Filter] | None = None,
        service: Service = Service.SPARKY,
    ):
        return self._client.create_entities(
            EntityType.DISTRIBUTOR, distributors, filters, service=service
        )

    def upload_pdf(  # noqa: C901
        self,
        distributor_id: int,
        pdf_path: str | None = None,
        pdf_bytes: bytes | None = None,
        mime_type: str | None = None,
        filename: str | None = None,
        preview_page_number: int | None = None,
        old_blob_id: str | None = None,
        **kwargs,
    ) -> Any:
        """
        Uploads a PDF file to a distributor and returns the blob ID.
        Does not add the PDF file to the distributor.

        Args:
            distributor_id (int): The unique identifier of the distributor.
            pdf_path (str | None): The local file path to the PDF file.
            pdf_bytes (bytes | None): The binary data of the PDF file.
            mime_type (str | None): The MIME type of the PDF file.
            filename (str | None): The name of the PDF file.
            preview_page_number (int | None): The page number for the preview image.
            old_blob_id (str | None): The blob ID of the existing PDF file.
            **kwargs: Additional keyword arguments containing PDF metadata.

        Returns:
            Any: The response data from the server.
            For example:
                {
                    "pdf_blob_id": "m-on/310089/pdf/file.pdf",
                    "pdf_mime_type": "application/pdf",
                    "pdf_size": 123456,
                    "pdf_page_count": 3,
                    "preview_image_blob_id":
                        "m-on/310089/pdf/image.jpg",
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
            response = client.distributors.upload_pdf(
                distributor_id=12345,
                pdf_path="/path/to/pdf_file.pdf"
            )

            # Upload a PDF file using binary data
            response = client.distributors.upload_pdf(
                distributor_id=12345,
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
        dist_pdf_upload_url = DISTRIBUTOR_PDF_UPLOAD_ENDPOINT.format(
            distributor_id=distributor_id
        )
        url = f"{self._client._base_url}{dist_pdf_upload_url}"
        params = {}
        if old_blob_id:
            old_extension = extract_extension_from_blob_id(old_blob_id)
            old_mime_type = extract_mime_type_from_extension(old_extension)
            if old_mime_type == content_type:
                params["old_blob_id"] = old_blob_id
        if preview_page_number:
            params["preview_page_number"] = preview_page_number
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
        distributor_id: int,
        pdf_title: str | None = None,
        old_blob_id: str | None = None,
    ) -> Any:
        """
        Requests a signed URL for uploading a PDF file to GCS.
        This method sends a request to Lydia for a signed URL that can be used to
        upload a PDF file to Google Cloud Storage (GCS). The signed URL is returned
        in the response, along with the blob ID and blob name.

        Args:
            distributor_id (int): The unique identifier of the distributor.
            pdf_title (str | None): The title of the PDF file. Optional.
            old_blob_id (str | None): The blob ID of the existing PDF file. Optional.
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
            response = client.distributors.get_pdf_signed_url(
                distributor_id=12345,
                pdf_title="Sample PDF",
                old_blob_id="m-on/310089/pdf/file.pdf"
            )
            ```
        """
        dist_pdf_signed_url_pathname = DISTRIBUTOR_PDF_SIGNED_URL_ENDPOINT.format(
            distributor_id=distributor_id
        )
        url = f"{self._client._base_url}{dist_pdf_signed_url_pathname}"
        params = {}
        if pdf_title:
            params["pdf_title"] = pdf_title
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
        distributor_id: int,
        mime_type: str,
        old_blob_id: str | None = None,
    ) -> Any:
        """
        Requests a signed URL for uploading a PDF preview image to GCS.
        This method sends a request to Lydia for a signed URL that can be used to
        upload a PDF preview image to Google Cloud Storage (GCS). The signed URL is
        returned in the response, along with the blob ID and blob name.

        Args:
            distributor_id (int): The unique identifier of the distributor.
            mime_type (str): The MIME type of the preview image.
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
            response = client.distributors.get_pdf_preview_signed_url(
                distributor_id=12345,
                mime_type="image/jpeg",
                old_blob_id="m-on/310089/pdf/image.jpg"
            )
            ```
        """
        dist_pdf_preview_signed_url_pathname = (
            DISTRIBUTOR_PDF_PREVIEW_SIGNED_URL_ENDPOINT.format(
                distributor_id=distributor_id
            )
        )
        url = f"{self._client._base_url}{dist_pdf_preview_signed_url_pathname}"
        params = {}
        if old_blob_id:
            params["old_blob_id"] = old_blob_id
        if mime_type:
            params["mime_type"] = mime_type
        if params:
            url += "?" + urlencode(params)
        resp = self._client._do_request("POST", url)
        if resp.status != 200:
            raise Exception(
                f"Failed to get signed URL. Status code: {resp.status}. {resp.data}"
            )
        return json.loads(resp.data.decode("utf-8"))
