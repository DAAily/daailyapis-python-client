from enum import Enum


class LucyEndpoint(str, Enum):
    MANUFACTURER = "/manufacturers"
    DISTRIBUTOR = "/distributors"
    COLLECTION = "/collections"
    JOURNALIST = "/journalists"
    MATERIAL = "/materials"
    PROJECT = "/projects"
    PRODUCT = "/products"
    FAMILY = "/families"
    CREATOR = "/creators"
    FILTER = "/filters"
    STORY = "/stories"
    SPACE = "/spaces"
    GROUP = "/groups"
    FAIR = "/fairs"


class Status(str, Enum):
    PREVIEW = "preview"
    ONLINE = "online"
    OFFLINE = "offline"
    DELETED = "deleted"
