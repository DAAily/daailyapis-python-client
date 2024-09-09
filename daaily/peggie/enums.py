from enum import Enum


class PeggieEndpoint(str, Enum):
    PREDICT_IMAGE_ENTITY_NAMES = "/predict-image-entity-names"
    PREDICT_IMAGE_USAGE_TEMP_ID = "/predict-image-usage-temp-id"
    PREDICT_IMAGE_ARCHITONIC_IDS = "/predict-image-architonic-ids"
