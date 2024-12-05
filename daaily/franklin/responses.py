from dataclasses import dataclass, field


@dataclass
class PredictGroupResponse:
    status: str = field()
    headers: dict = field()
    data: dict = field()

    @classmethod
    def from_response(cls, response):
        return cls(
            status=response.status,
            headers=response.headers,
            data=response.data,
        )
