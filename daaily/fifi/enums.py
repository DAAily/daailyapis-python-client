from enum import Enum


class FifiProcessType(str, Enum):
    IMAGES = "images"
    ENRICH = "enrich"


class FifiEndpoint(str, Enum):
    PREDICT_IMAGE_TYPE = "/predict-image-type"
    PREDICT_SPACE_TYPE = "/predict-space-type"
    EXTRACT_METADATA = "/extract-metadata"
    TYPE_METADATA = "/type-metadata"
    TYPE_COLOR = "/type-color"
    FIFI = "/fifi"
