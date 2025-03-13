import ast
import re
from typing import Any

from .type import AttributeType, AttributeValueType


def generate_unique_name(name: str):
    # Remove all non-alphanumeric characters (except spaces)
    name = name.replace(",", "_")  # special case because of this 3,5 mm -> 3_5_mm
    name = name.replace(
        " - ", "_"
    )  # special case for WBT - 0708 Cu nextgen™ -> wbt_0708_cu_nextgen
    name = name.replace("-", "_")  # special case for KNX-Systems -> knx_systems
    normalized_name = re.sub(r"[^\w\s]", "", name)
    normalized_name = normalized_name.lower().replace("  ", "_").replace(" ", "_")
    return normalized_name


def gen_attribute_name(name_en: str, attribute_type: AttributeType) -> str:
    name_lower_case = name_en.lower()
    # case like 5-star base -> base_5_star and not -> base_5_star_base
    name = name_lower_case.replace(
        attribute_type.value + "s", ""
    )  # special case Tabletop natural materials -> material_tabletop_natural_s
    name = name.replace(attribute_type.value, "")
    name = name.replace("colour", "")  # special case for British English
    name = name.replace("+", "plus")  # special case + 4-seater -> plus_4_seater
    name = name.replace(
        "<", "less_than"
    )  # special case < 4-seater -> less_than_4_seater
    name = name.replace(">", "greater_than")
    name = name.replace(",", "_")  # special case because of this 3,5 mm -> 3_5_mm
    name = name.replace(
        " - ", "_"
    )  # special case for WBT - 0708 Cu nextgen™ -> wbt_0708_cu_nextgen
    name = name.replace("-", "_")  # special case for KNX-Systems -> knx_systems
    name = name.strip()  # remove leading and trailing whitespaces
    if name.endswith("_"):
        name = name[:-1]
    if name.startswith("_"):
        name = name[1:]
    name = attribute_type.value + "_" + name
    unique_name = generate_unique_name(name)
    return unique_name


def custom_parse_string(value: str) -> Any:
    """
    Handle special-case strings that aren't valid Python literals.
    For instance, 'yes' or 'no' (in any case) can be converted to booleans,
    and 'none' can be converted to None.
    """
    lower_val = value.lower().strip()
    if lower_val in ("yes", "true", "none", "null", "undefined"):
        return True
    if lower_val in ("no", "false"):
        return False
    if lower_val == "none":
        return None
    return value


def try_parse_value(value: Any) -> Any:
    """
    If the input is a string, first try to safely evaluate it as a Python literal.
    If that fails (e.g. for custom cases like "yes"), then use custom logic.
    Otherwise, return the original value.
    """
    if isinstance(value, str):
        try:
            parsed_value = ast.literal_eval(value)
            return parsed_value
        except (ValueError, SyntaxError):
            return custom_parse_string(value)
    return value


def determine_attribute_value_type(value: Any) -> tuple[Any, AttributeValueType]:
    """
    Determine the attribute value type by first attempting to parse the input,
    then checking against a series of type conditions.
    """
    parsed_value = try_parse_value(value)
    if parsed_value is None:
        return parsed_value, AttributeValueType.BOOLEAN
    if isinstance(parsed_value, bool):
        return parsed_value, AttributeValueType.BOOLEAN
    if isinstance(parsed_value, (int, float)):
        return parsed_value, AttributeValueType.NUMBER
    if (
        isinstance(parsed_value, (list, tuple))
        and len(parsed_value) == 2
        and all(isinstance(x, (int, float)) for x in parsed_value)
    ):
        return parsed_value, AttributeValueType.NUMBER_RANGE
    if isinstance(parsed_value, list) and all(isinstance(x, str) for x in parsed_value):
        return parsed_value, AttributeValueType.LIST_STRINGS
    if isinstance(parsed_value, str):
        return parsed_value, AttributeValueType.STRING
    raise ValueError(f"Unsupported attribute value type: {value!r}")
