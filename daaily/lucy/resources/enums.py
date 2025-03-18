from enum import Enum


class AttributeType(Enum):
    """
    Based on corresponding attribute types from Lucy Repository here:
    https://github.com/DAAily/lucy-data-processing-api/blob/main/app/settings/enums/attribute_enums.py#L7
    """

    BASE = "base"
    CATEGORY = "category"
    CERTIFICATION = "certification"
    COLOR = "color"
    DECOR = "decor"
    DIMENSION = "dimension"
    FEATURE = "feature"
    MATERIAL = "material"
    OPTIC = "optic"
    STYLE = "style"
    USAGE = "usage"


class AttributeValueType(Enum):
    """
    Based on corresponding attribute types from Lucy Repository here:
    https://github.com/DAAily/lucy-data-processing-api/blob/main/app/settings/enums/attribute_enums.py#L22
    """

    BOOLEAN = "boolean"
    LIST_STRINGS = "list_strings"
    LIST_NUMBERS = "list_numbers"
    NUMBER = "number"
    NUMBER_RANGE = "number_range"
    STRING = "string"


class AttributeValueUnit(Enum):
    """
    Enumeration of standard units for attribute values.
    Based on corresponding attribute types from Lucy Repository here:
    https://github.com/DAAily/lucy-data-processing-api/blob/main/app/settings/enums/attribute_enums.py#L31
    """

    # Length units
    CM = "cm"  # centimeter
    M = "m"  # meter
    MM = "mm"  # millimeter
    KM = "km"  # kilometer
    INCH = "inch"  # inch

    # Weight units
    G = "g"  # gram
    KG = "kg"  # kilogram
    T = "t"  # ton
    MG = "mg"  # milligram

    # Electrical units
    V = "V"  # volt
    W = "W"  # watt
    A = "A"  # ampere
    MA = "mA"  # milliampere

    K = "K"  # Kelvin
    LM = "lm"  # lumen
