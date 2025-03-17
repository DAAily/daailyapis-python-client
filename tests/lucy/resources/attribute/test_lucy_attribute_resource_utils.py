import pytest

from daaily.lucy.resources.attribute.utils import (
    custom_parse_string,
    determine_attribute_value_type,
    try_parse_value,
)
from daaily.lucy.resources.enums import AttributeValueType


#
# Tests for custom_parse_string
#
@pytest.mark.parametrize(
    "input_value,expected_output",
    [
        ("yes", True),
        ("YES", True),
        ("true", True),
        ("TrUe", True),
        ("no", False),
        ("false", False),
        ("NONE", True),
        ("null", True),
        ("undefined", True),
        ("some_string", "some_string"),  # returns the original string
        ("  yes  ", True),  # with extra spaces
    ],
)
def test_custom_parse_string(input_value, expected_output):
    assert custom_parse_string(input_value) == expected_output


#
# Tests for try_parse_value
#
@pytest.mark.parametrize(
    "input_value,expected_output",
    [
        # Valid Python literal strings
        ("123", 123),
        ("3.14", 3.14),
        ("True", True),
        ("False", False),
        ("None", None),
        # Invalid Python literal => fallback to custom_parse_string
        ("yes", True),
        ("no", False),
        ("something", "something"),
        # Already non-string
        (42, 42),
        ([1, 2], [1, 2]),
    ],
)
def test_try_parse_value(input_value, expected_output):
    assert try_parse_value(input_value) == expected_output


#
# Tests for determine_attribute_value_type
#
@pytest.mark.parametrize(
    "input_value,expected_parsed_value,expected_type",
    [
        # None => treat as BOOLEAN
        ("None", True, AttributeValueType.BOOLEAN),
        ("none", True, AttributeValueType.BOOLEAN),
        # Booleans
        ("True", True, AttributeValueType.BOOLEAN),
        ("False", False, AttributeValueType.BOOLEAN),
        (True, True, AttributeValueType.BOOLEAN),
        (False, False, AttributeValueType.BOOLEAN),
        # Single numbers
        ("123", 123, AttributeValueType.NUMBER),
        ("3.14", 3.14, AttributeValueType.NUMBER),
        (100, 100, AttributeValueType.NUMBER),
        (2.71, 2.71, AttributeValueType.NUMBER),
        # NUMBER_RANGE: exactly two numeric items
        ("[1, 2]", [1, 2], AttributeValueType.NUMBER_RANGE),
        ((1.0, 2.5), (1.0, 2.5), AttributeValueType.NUMBER_RANGE),
        # LIST_NUMBER: all numeric but length != 2
        ("[]", [], AttributeValueType.LIST_NUMBER),  # empty list
        ("[42]", [42], AttributeValueType.LIST_NUMBER),  # single element
        ("[1, 2, 3]", [1, 2, 3], AttributeValueType.LIST_NUMBER),  # three elements
        # LIST_STRINGS
        ("['a', 'b']", ["a", "b"], AttributeValueType.LIST_STRINGS),
        (["hello", "world"], ["hello", "world"], AttributeValueType.LIST_STRINGS),
        # Special-case booleans
        ("yes", True, AttributeValueType.BOOLEAN),
        ("no", False, AttributeValueType.BOOLEAN),
        # Plain string
        ("some_string", "some_string", AttributeValueType.STRING),
    ],
)
def test_determine_attribute_value_type(
    input_value, expected_parsed_value, expected_type
):
    parsed_value, attr_type = determine_attribute_value_type(input_value)
    assert parsed_value == expected_parsed_value
    assert attr_type == expected_type


def test_determine_attribute_value_type_unsupported():
    """
    If none of the conditions match, the function should raise ValueError.
    For example, if it's a list of mixed types, a dict type, etc.
    """
    with pytest.raises(ValueError):
        # Mixed-type list doesn't match NUMBER_RANGE, LIST_NUMBER, or LIST_STRINGS
        determine_attribute_value_type(["string", 2])

    with pytest.raises(ValueError):
        # A dict is not handled
        determine_attribute_value_type({"key": "value"})
