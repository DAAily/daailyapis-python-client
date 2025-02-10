from typing import TYPE_CHECKING

from daaily.lucy.models import Filter

if TYPE_CHECKING:
    from daaily.lucy.client import Client


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
