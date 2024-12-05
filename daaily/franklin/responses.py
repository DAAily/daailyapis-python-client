import json
from dataclasses import dataclass, field
from typing import Mapping

from daaily.transport import Response


@dataclass
class PredictGroupResponse:
    status: int = field()
    headers: Mapping[str, str] = field()
    data: dict = field()

    @classmethod
    def from_response(cls, response: Response) -> "PredictGroupResponse":
        return cls(
            status=response.status,
            headers=response.headers,
            data=json.loads(response.data.decode("utf-8")),
        )
