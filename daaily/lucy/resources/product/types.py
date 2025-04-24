from dataclasses import dataclass
from typing import Any

from ..enums import AttributeType, AttributeValueUnit


@dataclass
class ProductAttribute:
    type: AttributeType
    value: Any
    value_unit: AttributeValueUnit | None
    options: list[str] | None
    name_en: str
    name_de: str | None
    name_fr: str | None
    name_es: str | None
    name_it: str | None
    description_en: str | None
    description_de: str | None
    description_it: str | None
    description_es: str | None
    description_fr: str | None
    synonyms_en: list[str] | None
    synonyms_de: list[str] | None
    synonyms_fr: list[str] | None
    synonyms_es: list[str] | None
    synonyms_it: list[str] | None
    platforms: list[str] | None
    status: str
