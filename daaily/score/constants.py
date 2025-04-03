from daaily.enums import Language

PRODUCT_WEIGHTS = {
    "internal_number": 0.01,
    "images": 0.2,
    "family_id": 0.05,
    "group_ids": 0.05,
    "attributes": 0.1,
    "collection_ids": 0.05,
    "text_en": 0.2175,
    "text_de": 0.2175,
    "text_es": 0.01,
    "text_fr": 0.01,
    "text_it": 0.01,
    "prices": 0.025,
    "pdfs": 0.025,
    "cads": 0.025,
    "materials": 0.0,  # materials are already included in attributes
    "3D": 0.0,  # 3d configs such as emersya, pcon config, etc
    "dimensions": 0.0,  # dimensions are already included in attributes
    "_": 0.0,
}

TEXT_SIMILARITY_TOPICS = {
    Language.EN: {
        "material": (
            "The text should describe the materials and colors used in the product. "
            + "Sample materials are wood, fabric, leather, metal, plastic, glass, etc.",
            0.3,
        ),
        "dimensions": (
            "The text should provide information about the dimensions of the product "
            + "like height, width, length but also weight",
            0.3,
        ),
        "usage": (
            "The text describes the usage of the product. Like at home, "
            + "in the office, outdoor, in living room also in bedroom, etc.",
            0.3,
        ),
        "audience": (
            "Who is using the product: all type of people, end users, man, women, "
            + "kid only, people outside, target audience etc.",
            0.1,
        ),
    },
    Language.DE: {
        "material": (
            "Der Text sollte die Materialien und Farben beschreiben, "
            + "die im Produkt verwendet werden. Beispielmaterialien sind "
            + "Holz, Stoff, Leder, Metall, Kunststoff, Glas usw.",
            0.3,
        ),
        "dimensions": (
            "Der Text sollte Informationen über die Abmessungen des Produkts wie "
            + "Höhe, Breite, Länge, aber auch Gewicht enthalten",
            0.3,
        ),
        "usage": (
            "Der Text beschreibt die Verwendung des Produkts. Wie zu Hause, im Büro, "
            + "im Freien, im Wohnzimmer, auch im Schlafzimmer, usw.",
            0.3,
        ),
        "audience": (
            "Wer das Produkt benutzt: alle Arten von Menschen, Endbenutzer, "
            + "Männer, Frauen, nur Kinder, Menschen im Freien, Zielgruppe usw.",
            0.1,
        ),
    },
    Language.ES: {
        "material": (
            "El texto debe describir los materiales y colores utilizados "
            + "en el producto. Ejemplos de materiales son madera, tela, cuero, "
            + "metal, plástico, vidrio, etc.",
            0.3,
        ),
        "dimensions": (
            "El texto debe proporcionar información sobre las dimensiones "
            + "del producto como altura, ancho, longitud pero también peso",
            0.3,
        ),
        "usage": (
            "El texto describe el uso del producto. Como en casa, en la oficina, "
            + "al aire libre, en la sala de estar también en el dormitorio, etc.",
            0.3,
        ),
        "audience": (
            "Quién utiliza el producto: todo tipo de personas, usuarios finales, "
            + "hombres, mujeres, solo niños, personas en exteriores, "
            + "público objetivo, etc.",
            0.1,
        ),
    },
    Language.FR: {
        "material": (
            "Le texte doit décrire les matériaux et les couleurs utilisés dans "
            + "le produit. Exemples de matériaux : bois, tissu, cuir, "
            + "métal, plastique, verre, etc.",
            0.3,
        ),
        "dimensions": (
            "Le texte doit fournir des informations sur les dimensions du "
            + "produit comme la hauteur, la largeur, la longueur mais aussi le poids",
            0.3,
        ),
        "usage": (
            "Le texte décrit l'utilisation du produit. Comme à la maison, au bureau, "
            + "en extérieur, dans le salon, aussi dans la chambre, etc.",
            0.3,
        ),
        "audience": (
            "Qui utilise le produit : tous types de personnes, utilisateurs "
            + "finaux, hommes, femmes, enfants uniquement,"
            + " personnes à l'extérieur, public cible, etc.",
            0.1,
        ),
    },
    Language.IT: {
        "material": (
            "Il testo dovrebbe descrivere i materiali e i colori utilizzati nel "
            + "prodotto. Esempi di materiali sono legno, tessuto, pelle, "
            + "metallo, plastica, vetro, ecc.",
            0.3,
        ),
        "dimensions": (
            "Il testo dovrebbe fornire informazioni sulle dimensioni del prodotto come "
            + "altezza, larghezza, lunghezza ma anche peso",
            0.3,
        ),
        "usage": (
            "Il testo descrive l'utilizzo del prodotto. Come a casa, in ufficio, "
            + "all'aperto, in soggiorno, anche in camera da letto, ecc.",
            0.3,
        ),
        "audience": (
            "Chi utilizza il prodotto: tutti i tipi di persone, utenti finali, "
            + "uomini, donne, solo bambini, persone all'esterno, pubblico target, ecc.",
            0.1,
        ),
    },
}
