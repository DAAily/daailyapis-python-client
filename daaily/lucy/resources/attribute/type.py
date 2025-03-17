from dataclasses import dataclass

from ..enums import AttributeType, AttributeValueType, AttributeValueUnit


@dataclass
class AttributeBase:
    type: AttributeType
    value_type: AttributeValueType
    value_unit: AttributeValueUnit | None
    options: list[str] | None
    name_en: str
    name_de: str | None
    name_fr: str | None
    name_es: str | None
    name_it: str | None
    old_group_ids: list[int] | None
    old_group_ids_opposite: list[int] | None
    old_filter_id: int | None
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
    opposite_name_en: str | None
    opposite_name_de: str | None
    opposite_name_fr: str | None
    opposite_name_es: str | None
    opposite_name_it: str | None
    platforms: list[str] | None
    status: str
