from daaily.credentials_sally import Credentials
from daaily.franklin.responses import PredictGroupResponse
from daaily.transport import Response
from daaily.transport.urllib3_http import AuthorizedHttp

FRANKLIN_V1_BASE_URL = "https://franklin.daaily.com/api/v1"


class Client:
    """
    The Franklin client is used to interact with the Franklin server.
    It provides functionality in order to make requests to each of Franklin's endpoints
    including the ability to create, update, and delete objects.
    You will also be able to specify to either use the client in a synchronous or
    asynchronous manner.
    """

    def __init__(
        self,
        credentials: Credentials | None = None,
        http=None,
        base_url: str | None = None,
    ):
        """
        Creates a new Franklin client.
        """
        if credentials is None:
            credentials = Credentials()
        self._credentials = credentials
        if base_url is None:
            base_url = FRANKLIN_V1_BASE_URL
        self._base_url = base_url
        if http is not None:
            """
            TODO: Add custom request handlers. That allows async requests.
            Needs to follow the same interface as the http_client. By implementing
            abc classes.
            """
            raise NotImplementedError("Custom request handlers are not supported yet.")
        self._auth_http = AuthorizedHttp(self._credentials)

    def _do_request(self, method, url, **kwargs) -> Response:
        """
        Makes a request to the server.
        """
        r = self._auth_http.request(method, url, **kwargs)
        return r

    def predict_product_group(
        self,
        image_path: str,
        product_name: str,
        product_text: str,
        model_type: str = "furniture",
    ) -> PredictGroupResponse:
        """
        Predicts the group of a product based on its image, name, and descriptive text.

        This method sends a POST request to the Franklin server to classify the product
        into a group.
        The request body is structured as follows:
        ```json
        [
            {
                "name": "<product_name>",
                "text": "<product_text>",
                "image_path": "<image_path>",
                "model_type": "furniture"
            }
        ]
        ```

        Parameters:
            image_path (str): Public accessable URL of the product image to be analyzed.
            product_name (str): The name of the product to be classified.
            product_text (str): Additional product descriptive text or attributes.

        Returns:
            dict: A dictionary containing the predicted group and associated metadata.
            Example response:
            ```json
            {
                "https://storage.googleapis.com/m-on/203/royal-botania_alura.jpeg": {
                    "level_3": {
                        "confidence": "0.8875133",
                        "confidence_class": "GREEN",
                        "id": "3237479",
                        "name": "Poufs"
                    },
                    "level_4": [
                        {
                            "confidence": "0.8746779",
                            "confidence_class": "GREEN",
                            "id": "3243675",
                            "name": "Closed base"
                        },
                        {
                            "confidence": "0.646546",
                            "confidence_class": "RED",
                            "id": "3243671",
                            "name": "Seat upholstered"
                        }
                    ]
                }
            }
            ```

        Raises:
            json.JSONDecodeError: If the response body cannot be parsed as valid JSON
            TransportException: Connection errors, timeouts,or invalid server responses.
        """
        url = f"{self._base_url}/products/predict-group"
        response = self._do_request(
            "POST",
            url,
            json=[
                {
                    "image_path": image_path,
                    "name": product_name,
                    "text": product_text,
                    "model_type": model_type,
                }
            ],
        )
        return PredictGroupResponse.from_response(response)
