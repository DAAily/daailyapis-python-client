import ast
from typing import Any

from .type import AttributeType, AttributeValueType, AttributeValueUnit


def gen_new_attribute_object_with_extras(
    name_en: str,
    attribute_type: AttributeType,
    value_type: AttributeValueType,
    value_unit: AttributeValueUnit | None = None,
    **kwargs,
):
    return {
        "name_en": name_en,
        "type": attribute_type.value,
        "value_type": value_type.value,
        "value_unit": value_unit.value if value_unit else None,
        **kwargs,
    }


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
    # None or booleans
    if parsed_value is None:
        return True, AttributeValueType.BOOLEAN
    if isinstance(parsed_value, bool):
        return parsed_value, AttributeValueType.BOOLEAN
    # Single numbers
    if isinstance(parsed_value, (int, float)):
        return parsed_value, AttributeValueType.NUMBER
    # Lists or tuples
    if isinstance(parsed_value, (list, tuple)):
        # Check NUMBER_RANGE (exactly two numeric items)
        if len(parsed_value) == 2 and all(
            isinstance(x, (int, float)) for x in parsed_value
        ):
            return parsed_value, AttributeValueType.NUMBER_RANGE
        # Check LIST_STRINGS (all strings)
        if all(isinstance(x, str) for x in parsed_value):
            return parsed_value, AttributeValueType.LIST_STRINGS
        # If it's a list/tuple but doesn't match any known numeric or string pattern
        raise ValueError(f"Unsupported attribute value type: {value!r}")
    # Strings
    if isinstance(parsed_value, str):
        return parsed_value, AttributeValueType.STRING
    # If none of the above conditions match, raise an error
    raise ValueError(f"Unsupported attribute value type: {value!r}")
