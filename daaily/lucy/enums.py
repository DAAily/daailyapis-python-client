from enum import Enum


class Service(str, Enum):
    WOODSTOCK = "woodstock"
    SPARKY = "sparky"
    HAKODA = "hakoda"
    ROKU = "roku"
    HOOVER = "hoover"


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
    ATTRIBUTE = "attribute"
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


class AssetType(str, Enum):
    IMAGE = "image"
    PDF = "pdf"
    CAD = "cad"
    ABOUT = "about"  # relates to the images of the about section


class MimeType(Enum):
    PNG = "image/png"
    GIF = "image/gif"
    JPG = "image/jpeg"
    WEBP = "image/webp"
    TIFF = "image/tiff"
    SVG = "image/svg+xml"
    ICO = "image/x-icon"
    BMP = "image/bmp"
    PDF = "application/pdf"
    XLS = "application/vnd.ms-excel"
    XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    CSV = "text/csv"
    JSON = "application/json"
    JPEG = "image/jpeg"
    ICON = "image/x-icon"
    DWG = "image/vnd.dwg"
    ZIP = "application/zip"
    EPS = "application/postscript"
    OCTET_STREAM = "application/octet-stream"
    ICON_MICROSOFT = "image/vnd.microsoft.icon"

    @staticmethod
    def extract_from_extension(extension: str):  # noqa: C901
        if extension == "png":
            return MimeType.PNG
        if extension == "gif":
            return MimeType.GIF
        if extension == "jpg":
            return MimeType.JPG
        if extension == "jpeg":
            return MimeType.JPG
        if extension == "webp":
            return MimeType.WEBP
        if extension == "tiff":
            return MimeType.TIFF
        if extension == "svg":
            return MimeType.SVG
        if extension == "ico":
            return MimeType.ICO
        if extension == "bmp":
            return MimeType.BMP
        if extension == "pdf":
            return MimeType.PDF
        if extension == "xls":
            return MimeType.XLS
        if extension == "xlsx":
            return MimeType.XLSX
        if extension == "csv":
            return MimeType.CSV
        if extension == "json":
            return MimeType.JSON


class Language(str, Enum):
    EN = "en"
    DE = "de"
    ES = "es"
    FR = "fr"
    IT = "it"
