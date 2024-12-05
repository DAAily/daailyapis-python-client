from dataclasses import dataclass, field


@dataclass
class PredictGroupResponse:
    status: str = field()
    data: dict = field()

    @classmethod
    def from_response(cls, response):
        return cls(
            status=response.status,
            data=response.data,
        )
