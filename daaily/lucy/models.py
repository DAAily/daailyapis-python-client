from dataclasses import dataclass, field

from daaily.lucy.enums import QueryOperators


@dataclass
class Filter:
    name: str
    value: str
    operator: QueryOperators = field(default=QueryOperators.EQ)
