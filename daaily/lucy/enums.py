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
    PRODUCT = "product"
    GROUP = "group"
    FILTER = "filter"
    FAMILY = "family"
    COLLECTION = "collection"
    DISTRIBUTOR = "distributor"
    PROJECT = "project"
    STORY = "story"
    CREATOR = "creator"
