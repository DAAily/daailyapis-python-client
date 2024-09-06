from enum import Enum


class Environment(str, Enum):
    PRODUCTION = "production"
    STAGING = "staging"


class DaailyService(str, Enum):
    LUCY = "Lucy"
    FIFI = "Fifi"
    PEGGIE = "Peggie"
    SALLY = "Sally"
