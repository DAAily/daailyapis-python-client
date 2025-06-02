from enum import Enum


class AttributeType(str, Enum):
    """
    Based on corresponding attribute types from Lucy Repository here:
    https://github.com/DAAily/lucy-data-processing-api/blob/main/app/settings/enums/attribute_enums.py#L7
    """

    BASE = "base"
    CATEGORY = "category"
    CERTIFICATION = "certification"
    COLOR = "color"
    DIMENSION = "dimension"
    FEATURE = "feature"
    MATERIAL = "material"
    USAGE = "usage"


class AttributeValueType(str, Enum):
    """
    Based on corresponding attribute types from Lucy Repository here:
    https://github.com/DAAily/lucy-data-processing-api/blob/main/app/settings/enums/attribute_enums.py#L22
    """

    BOOLEAN = "boolean"
    LIST_STRINGS = "list_strings"
    NUMBER = "number"
    NUMBER_RANGE = "number_range"
    STRING = "string"


class AttributeValueUnit(str, Enum):
    """
    Enumeration of standard units for attribute values.
    Based on corresponding attribute types from Lucy Repository here:
    https://github.com/DAAily/lucy-data-processing-api/blob/main/app/settings/enums/attribute_enums.py#L31
    """

    # Length
    CM = "cm"  # centimeters

    # Weight
    KG = "kg"  # kilograms

    # Area
    SQ_M = "m^2"  # square meters

    # Volume
    CU_M = "m^3"  # cubic meters

    # Temperature
    C = "°C"  # degrees Celsius

    # Luminous Flux
    LM = "lm"  # lumens

    # Electrical
    V = "V"  # volts
    W = "W"  # watts
    A = "A"  # amperes

    # Angle
    DEG = "°"  # degrees
