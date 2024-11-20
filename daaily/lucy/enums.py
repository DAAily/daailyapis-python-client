from enum import Enum


class QueryOperators(str, Enum):
    EQ = "eq"
    NEQ = "neq"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    IN = "in"


class EntityType(str, Enum):
    MANUFACTURER = "manufacturer"
    DISTRIBUTOR = "distributor"
    COLLECTION = "collection"
    JOURNALIST = "journalist"
    MATERIAL = "material"
    PROJECT = "project"
    PRODUCT = "product"
    CREATOR = "creator"
    FAMILY = "family"
    FILTER = "filter"
    SPACE = "space"
    GROUP = "group"
    STORY = "story"
    FAIR = "fair"
