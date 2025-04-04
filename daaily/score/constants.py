from daaily.enums import Language

PRODUCT_WEIGHTS = {
    "images": 0.2,
    "attributes": 0.1,
    "internal_number": 0.0093,
    "family_id": 0.0467,
    "group_ids": 0.0467,
    "collection_ids": 0.0467,
    "text_en": 0.2031,
    "text_de": 0.203,
    "text_es": 0.0093,
    "text_fr": 0.0093,
    "text_it": 0.0093,
    "prices": 0.0233,
    "pdfs": 0.0233,
    "cads": 0.0233,
    "live_link": 0.0467,
}


TEXT_SIMILARITY_TOPICS = {
    Language.EN: {
        "benefits": (
            "The text should highlight the benefits and advantages of the product. "
            + "What problems does it solve? What makes it special or unique?",
            0.35,
        ),
        "design_concept": (
            "The text should explain the design philosophy, inspiration, or concept "
            + "behind the product. What was the designer's intent?",
            0.25,
        ),
        "experience": (
            "The text should describe the experience of using the product. "
            + "How it feels, enhances spaces, or creates atmosphere.",
            0.25,
        ),
        "context": (
            "The text should place the product in context - how it relates "
            + "to other pieces, environments, or design trends.",
            0.15,
        ),
    },
    Language.DE: {
        "benefits": (
            "Der Text sollte die Vorteile des Produkts hervorheben. "
            + "Welche Probleme löst es? Was macht es besonders oder einzigartig?",
            0.35,
        ),
        "design_concept": (
            "Der Text sollte die Design-Philosophie, Inspiration oder das Konzept "
            + "hinter dem Produkt erklären. Was war die Absicht des Designers?",
            0.25,
        ),
        "experience": (
            "Der Text sollte das Erlebnis der Nutzung des Produkts beschreiben. "
            + "Wie es sich anfühlt, Räume verbessert oder Atmosphäre schafft.",
            0.25,
        ),
        "context": (
            "Der Text sollte das Produkt in einen Kontext stellen - wie es sich "
            + "zu anderen Stücken, Umgebungen oder Design-Trends verhält.",
            0.15,
        ),
    },
    Language.ES: {
        "benefits": (
            "El texto debe destacar los beneficios y ventajas del producto. "
            + "¿Qué problemas resuelve? ¿Qué lo hace especial o único?",
            0.35,
        ),
        "design_concept": (
            "El texto debe explicar la filosofía de diseño, la inspiración o el "
            + "concepto detrás del producto. ¿Cuál fue la intención del diseñador?",
            0.25,
        ),
        "experience": (
            "El texto debe describir la experiencia de usar el producto. "
            + "Cómo se siente, mejora los espacios o crea atmósfera.",
            0.25,
        ),
        "context": (
            "El texto debe situar el producto en contexto - cómo se relaciona "
            + "con otras piezas, entornos o tendencias de diseño.",
            0.15,
        ),
    },
    Language.FR: {
        "benefits": (
            "Le texte doit mettre en évidence les avantages et les bénéfices "
            + "du produit. Quels problèmes résout-il ? Qu'est-ce qui le rend "
            + "spécial ou unique ?",
            0.35,
        ),
        "design_concept": (
            "Le texte doit expliquer la philosophie de design, l'inspiration ou "
            + "le concept derrière le produit. Quelle était l'intention du designer ?",
            0.25,
        ),
        "experience": (
            "Le texte doit décrire l'expérience d'utilisation du produit. "
            + "Comment il se ressent, améliore les espaces ou crée une atmosphère.",
            0.25,
        ),
        "context": (
            "Le texte doit placer le produit dans son contexte - comment il "
            + "se rapporte à d'autres pièces, environnements ou tendances de design.",
            0.15,
        ),
    },
    Language.IT: {
        "benefits": (
            "Il testo dovrebbe evidenziare i benefici e i vantaggi del prodotto. "
            + "Quali problemi risolve? Cosa lo rende speciale o unico?",
            0.35,
        ),
        "design_concept": (
            "Il testo dovrebbe spiegare la filosofia di design, l'ispirazione o "
            + "il concetto alla base del prodotto. Qual era l'intento del designer?",
            0.25,
        ),
        "experience": (
            "Il testo dovrebbe descrivere l'esperienza di utilizzo del prodotto. "
            + "Come si sente, come migliora gli spazi o crea atmosfera.",
            0.25,
        ),
        "context": (
            "Il testo dovrebbe collocare il prodotto nel contesto - come si relaziona "
            + "con altri pezzi, ambienti o tendenze di design.",
            0.15,
        ),
    },
}
