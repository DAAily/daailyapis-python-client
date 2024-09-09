from typing import Any

from pydantic import BaseModel, Field


class HttpResponse(BaseModel):
    data: Any = Field(default=...)
    status_code: int = Field(default=...)
    headers: Any = Field(default=...)
