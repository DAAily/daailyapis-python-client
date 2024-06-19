from urllib3 import BaseHTTPResponse, PoolManager


class Client:
    def __init__(self) -> None:
        self.http = PoolManager()

    def get_request(self, url: str, headers: dict | None) -> BaseHTTPResponse:
        response = self.http.request("GET", url, headers=headers)
        return response

    def post_request(
        self, url: str, body: dict | list | None, headers: dict | None
    ) -> BaseHTTPResponse:
        response = self.http.request("POST", url, json=body, headers=headers)
        return response

    def put_request(
        self, url: str, body: dict | list | None, headers: dict | None
    ) -> BaseHTTPResponse:
        response = self.http.request("PUT", url, json=body, headers=headers)
        return response

    def patch_request(
        self, url: str, body: dict | None, headers: dict | None
    ) -> BaseHTTPResponse:
        response = self.http.request("PATCH", url, json=body, headers=headers)
        return response

    def delete_request(
        self, url: str, body: dict | None, headers: dict | None
    ) -> BaseHTTPResponse:
        response = self.http.request("DELETE", url, json=body, headers=headers)
        return response
