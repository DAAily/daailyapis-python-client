import httpx


class Client:
    def __init__(self) -> None:
        self.http_async = httpx.AsyncClient(timeout=3600)

    # ASYNC

    async def get_request(self, url: str, headers: dict | None) -> httpx.Response:
        response = await self.http_async.request("GET", url, headers=headers)
        return response

    async def post_request(
        self, url: str, body: dict | list | None, headers: dict | None
    ) -> httpx.Response:
        response = await self.http_async.request(
            "POST", url, json=body, headers=headers
        )
        return response

    async def put_request(
        self, url: str, body: dict | list | None, headers: dict | None
    ) -> httpx.Response:
        response = await self.http_async.request("PUT", url, json=body, headers=headers)
        return response

    async def patch_request(
        self, url: str, body: dict | None, headers: dict | None
    ) -> httpx.Response:
        response = await self.http_async.request(
            "PATCH", url, json=body, headers=headers
        )
        return response

    async def delete_request(
        self, url: str, body: dict | None, headers: dict | None
    ) -> httpx.Response:
        response = await self.http_async.request(
            "DELETE", url, json=body, headers=headers
        )
        return response
