PRODUCT_WEIGHTS = {
    "internal_number": 0.01,
    "images": 0.2,
    "family_id": 0.05,
    "group_ids": 0.05,
    "materials": 0.05,
    "attributes": 0.1,
    "collection_ids": 0.05,
    "text_en": 0.3,
    "3D": 0.05,
    "dimensions": 0.05,
    "prices": 0.025,
    "pdfs": 0.025,
    "cads": 0.025,
    "_": 0.015,  # the max value will bei 88.5
}

TEXT_SIMILARITY_TOPICS = {
    "material": (
        "The text should describe the materials and colors used in the product. Sample "
        + "materials are wood, fabric,leather, metal, plastic, glass, etc.",
        0.3,
    ),
    "dimensions": (
        "The text should provide information about the dimensions of the product like "
        + "height, width,length but also weigth",
        0.3,
    ),
    "usage": (
        "The text descibes the usage of the product. Like at home, in the office, "
        + "outdoor, in living room also in bedroom, etc.",
        0.3,
    ),
    "audience": (
        "Who is using the product: all type of people, end users, man, women, kid only,"
        + " people outside. target audience etc.",
        0.1,
    ),
}
