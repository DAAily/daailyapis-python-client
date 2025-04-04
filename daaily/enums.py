from enum import Enum


class Language(str, Enum):
    """
    Enum for DAAily supported languages.

    Please make sure these languages are a subset of
    https://cloud.google.com/natural-language/docs/languages#v2_model
    """

    EN = "en"
    DE = "de"
    ES = "es"
    FR = "fr"
    IT = "it"
