from daaily.lucy.enums import AssetType, EntityType

entity_type_endpoint_mapping = {
    EntityType.MANUFACTURER: "manufacturers",
    EntityType.DISTRIBUTOR: "distributors",
    EntityType.INSTITUTION: "institutions",
    EntityType.COLLECTION: "collections",
    EntityType.JOURNALIST: "journalists",
    EntityType.ATTRIBUTE: "attributes",
    EntityType.MATERIAL: "materials",
    EntityType.PROJECT: "projects",
    EntityType.PRODUCT: "products",
    EntityType.CREATOR: "creators",
    EntityType.FAMILY: "families",
    EntityType.FILTER: "filters",
    EntityType.STORY: "stories",
    EntityType.SPACE: "spaces",
    EntityType.GROUP: "groups",
}

MIME_TYPE_TO_ASSET_TYPE = {
    # CAD-related
    "application/octet-stream": AssetType.CAD,
    "image/vnd.dwg": AssetType.CAD,
    "application/zip": AssetType.CAD,
    "application/x-3ds": AssetType.CAD,
    "application/vnd.sketchup.skp": AssetType.CAD,
    "model/vnd.collada+xml": AssetType.CAD,
    "image/vnd.dxf": AssetType.CAD,
    "model/obj": AssetType.CAD,
    "model/stl": AssetType.CAD,
    "model/gltf+json": AssetType.CAD,
    "model/gltf-binary": AssetType.CAD,
    "text/plain": AssetType.CAD,
    # PDF (additional known variants)
    "application/pdf": AssetType.PDF,
    "application/x-pdf": AssetType.PDF,  # less common, fallback
    # Images (additional variants and fallbacks)
    "image/jpeg": AssetType.IMAGE,
    "image/png": AssetType.IMAGE,
    "image/gif": AssetType.IMAGE,
    "image/bmp": AssetType.IMAGE,
    "image/tiff": AssetType.IMAGE,
    "image/webp": AssetType.IMAGE,
    "image/x-icon": AssetType.IMAGE,
    "image/svg+xml": AssetType.IMAGE,
}

ENTITY_ASSET_TYPE_UPLOADS_ENDPOINT_MAPPING = {
    (EntityType.MANUFACTURER, AssetType.IMAGE): "manufacturers/images",
    (EntityType.MANUFACTURER, AssetType.PDF): "manufacturers/pdfs",
    (EntityType.MANUFACTURER, AssetType.CAD): "manufacturers/cads",
    (EntityType.DISTRIBUTOR, AssetType.IMAGE): "distributors/images",
    (EntityType.DISTRIBUTOR, AssetType.PDF): "distributors/pdfs",
    (EntityType.DISTRIBUTOR, AssetType.CAD): "distributors/cads",
    (EntityType.COLLECTION, AssetType.IMAGE): "collections/images",
    (EntityType.COLLECTION, AssetType.PDF): "collections/pdfs",
    (EntityType.COLLECTION, AssetType.CAD): "collections/cads",
    (EntityType.JOURNALIST, AssetType.IMAGE): "journalists/images",
    (EntityType.JOURNALIST, AssetType.PDF): "journalists/pdfs",
    (EntityType.JOURNALIST, AssetType.CAD): "journalists/cads",
    (EntityType.MATERIAL, AssetType.IMAGE): "materials/images",
    (EntityType.MATERIAL, AssetType.PDF): "materials/pdfs",
    (EntityType.MATERIAL, AssetType.CAD): "materials/cads",
    (EntityType.PROJECT, AssetType.IMAGE): "projects/images",
    (EntityType.PROJECT, AssetType.PDF): "projects/pdfs",
    (EntityType.PROJECT, AssetType.CAD): "projects/cads",
    (EntityType.PRODUCT, AssetType.IMAGE): "products/{entity_id}/uploads/image",
    (EntityType.PRODUCT, AssetType.PDF): "products/{entity_id}/uploads/pdf",
    (EntityType.PRODUCT, AssetType.CAD): "products/{entity_id}/uploads/cad",
    (EntityType.CREATOR, AssetType.IMAGE): "creators/images",
    (EntityType.CREATOR, AssetType.PDF): "creators/pdfs",
    (EntityType.CREATOR, AssetType.CAD): "creators/cads",
    (EntityType.FAMILY, AssetType.IMAGE): "families/images",
    (EntityType.FAMILY, AssetType.PDF): "families/pdfs",
    (EntityType.FAMILY, AssetType.CAD): "families/cads",
    (EntityType.FILTER, AssetType.IMAGE): "filters/images",
    (EntityType.FILTER, AssetType.PDF): "filters/pdfs",
    (EntityType.FILTER, AssetType.CAD): "filters/cads",
    (EntityType.STORY, AssetType.IMAGE): "stories/images",
    (EntityType.STORY, AssetType.PDF): "stories/pdfs",
    (EntityType.STORY, AssetType.CAD): "stories/cads",
    (EntityType.SPACE, AssetType.IMAGE): "spaces/images",
    (EntityType.SPACE, AssetType.PDF): "spaces/pdfs",
    (EntityType.SPACE, AssetType.CAD): "spaces/cads",
    (EntityType.GROUP, AssetType.IMAGE): "groups/images",
    (EntityType.GROUP, AssetType.PDF): "groups/pdfs",
    (EntityType.GROUP, AssetType.CAD): "groups/cads",
}
