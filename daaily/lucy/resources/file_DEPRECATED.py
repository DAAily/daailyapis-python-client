import os

from typing_extensions import deprecated

from daaily.lucy.utils import get_asset_type_from_mime_type, get_file_data_and_mimetype

from . import BaseResource

FILE_UPLOADS_UNSPECIFIC_ENDPOINT = "/files/uploads/temp/unspecific"


@deprecated("This resource is deprecated and will be removed in a future version.")
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
        file_data, mime_type, _ = get_file_data_and_mimetype(file_path)
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
