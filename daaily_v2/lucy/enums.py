from enum import Enum


class LucyEndpoint(str, Enum):
    MANUFACTURER = "/manufacturers"
    DISTRIBUTOR = "/distributors"
    COLLECTION = "/collections"
    JOURNALIST = "/journalists"
    PROJECT = "/projects"
    PRODUCT = "/products"
    FAMILY = "/families"
    CREATOR = "/creators"
    FILTER = "/filters"
    STORY = "/stories"
    GROUP = "/groups"
    FAIR = "/fairs"
