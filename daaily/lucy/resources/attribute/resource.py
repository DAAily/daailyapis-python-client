from typing import Any, Dict, Generator, Literal

from daaily.lucy.enums import EntityType, Service
from daaily.lucy.models import Filter

from .. import BaseResource
from .types import AttributeType, AttributeValueType, AttributeValueUnit
from .utils import determine_attribute_value_type, gen_new_attribute_object_with_extras


class AttributesResource(BaseResource):
    def get(
        self, filters: list[Filter] | None = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Retrieves attributes with optional filtering, returning them as a generator
        that yields each attribute one at a time.

        Available filters:
            - attribute_ids (str): Filter by comma separated attribute IDs.
            - old_group_ids (str): Filter by comma separated old group IDs.
            - type (str): Filter by attribute type. Available values: base, category,
              certification, color, decor, dimension, feature, material, optic, style,
              usage
            - names (str): Filter by comma separated names.
            - synonyms (str): Filter by comma separated synonyms.

        Note that the following filters are automatically added to the query:
            - skip (int): Number of records to skip.
            - limit (int): Maximum number of records to retrieve.

        Args:
            filters (list[Filter] | None): A list of filters to apply to the query.

        Yields:
            dict: A dictionary representing a single attribute.

        Example:
            ```python
            # Define filters
            filters = [Filter("type", "feature")]

            # Get attributes (pagination handled internally)
            attributes = client.attributes.get(filters=filters)

            # Iterate over the results without worrying about pagination
            for a in attributes:
                print(f"ID: {a['attribute_id']}, Name: {a['name_en']}")
            ```
        """
        if filters is None:
            filters = []
        limit_value = "100"
        skip_value = "0"
        new_filters = []
        for f in filters:
            if f.name == "limit":
                limit_value = f.value
            elif f.name == "skip":
                skip_value = f.value
            else:
                new_filters.append(f)
        limit_filter = Filter(name="limit", value=limit_value)
        skip_filter = Filter(name="skip", value=skip_value)
        new_filters.append(limit_filter)
        new_filters.append(skip_filter)
        while True:
            response = self._client.get_entities(EntityType.ATTRIBUTE, new_filters)
            if response.status != 200:
                break
            for item in response.json():  # type: ignore
                yield item
            skip_value = str(int(skip_value) + int(limit_value))
            skip_filter.value = skip_value
            new_filters = [f for f in new_filters if f.name != "skip"]
            new_filters.append(skip_filter)

    def search(
        self,
        query: str,
        mode: Literal["keyword", "hybrid", "vector"] = "keyword",
        filters: list[Filter] | None = None,
        return_type: Literal["json", "response"] = "response",
    ) -> list[dict] | Any:
        """
        Searches for attributes based on a query string.

        Args:
            query (str): The search query string.
            mode (str): The search mode. Available values: "keyword", "hybrid",
                "vector".

        Returns:
            list[dict]: A list of attributes matching the search criteria.

        Example:
            ```python
            results = client.attributes.search("example attribute")
            for attribute in results:
                print(attribute)
            ```
        """
        response = self._client.search_entities(
            EntityType.ATTRIBUTE, query, mode, filters=filters
        )
        if return_type == "json":
            if response.status != 200:
                raise Exception(
                    f"Error: {response.status} - {response.data.decode('utf-8')}"
                )
            return response.json()
        return response

    def get_by_id(self, attribute_id: int):
        return self._client.get_entity(EntityType.ATTRIBUTE, attribute_id)

    def get_by_name(self, name: str):
        return self._client.get_entity_custom(EntityType.ATTRIBUTE, name, "name")

    def update(self, attributes: list[dict], service: Service = Service.SPARKY):
        """
        Updates existing attribute objects.

        This function allows for the updating of one or more attributes in the system.
        Each attribute to be updated is defined as a dictionary that must include an
        identifier (such as "id" or another unique key) along with the keys representing
        the properties to be updated (e.g., "name", "type", "value_type", etc.).

        NOTE: Attribute type and name_en cannot be updated. If you need to change these
          values, you must create a new attribute and delete the old one.

        Args:
            attributes (list[dict]): A list of attribute objects to update.
                Each attribute dictionary should include an identifier
                (e.g., "attribute_id") and any of the following keys if they need to be
                updated:
                {
                  "attribute_id": int,  # Unique identifier of the attribute to update
                  "value_type": "boolean" | "number" | "string" | "list" | "range",
                  "value_unit": "cm" | "m" | "mm" | "inch",
                  "options": [
                    "string"
                  ],
                  "name_de": "string",
                  "name_fr": "string",
                  "name_es": "string",
                  "name_it": "string",
                  "description_en": "string",
                  "description_de": "string",
                  "description_it": "string",
                  "description_es": "string",
                  "description_fr": "string",
                  "synonyms_en": [
                    "string"
                  ],
                  "synonyms_de": [
                    "string"
                  ],
                  "synonyms_fr": [
                    "string"
                  ],
                  "synonyms_es": [
                    "string"
                  ],
                  "synonyms_it": [
                    "string"
                  ],
                  "opposite_name_en": "string",
                  "opposite_name_de": "string",
                  "opposite_name_fr": "string",
                  "opposite_name_es": "string",
                  "opposite_name_it": "string",
                  "platforms": [
                    "new_architonic", "architonic", "archdaily", "daaily-index"
                  ],
                  "status": "online",
                  "revision_uuid": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
                }

        Raises:
            Exception: If the attribute update process fails due to invalid input,
                missing identifiers, or other errors.

        Returns:
            Any: The result of the attribute update process, which may include details
                of the updated attributes.

        Example:
            ```python
            attributes_update_data = [
                {
                    "attribute_id": 123,
                    "name_en": "Updated Attribute Name",
                    "name_de": "Aktualisierter Attributname",
                    "name_fr": "Nom de l'attribut mis à jour",
                    "name_es": "Nombre de atributo actualizado",
                    "name_it": "Nome dell'attributo aggiornato",
                    "description_en": "Updated description for the attribute",
                    "description_de": "Aktualisierte Beschreibung für das Attribut",
                    "description_fr": "Description mise à jour pour l'attribut",
                    "description_es": "Descripción actualizada para el atributo",
                    "description_it": "Descrizione aggiornata per l'attributo",
                    "synonyms_en": ["Updated", "Modified"],
                    "synonyms_de": ["Aktualisiert"],
                    "synonyms_fr": ["Mis à jour"],
                    "synonyms_es": ["Actualizado"],
                    "synonyms_it": ["Aggiornato"],
                    "platforms": [
                      "new_architonic", "architonic", "archdaily", "daaily-index"
                    ],
                    "status": "online",
                    "revision_uuid": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
                }
            ]

            result = client.attributes.update(attributes=attributes_update_data)
            ```
        """
        return self._client.update_entities(
            EntityType.ATTRIBUTE, attributes, service=service
        )

    def create(self, attributes: list[dict], service: Service = Service.SPARKY):
        """
        Creates new attribute objects.

        This function allows for the creation of one or more new attributes in the
        system. Each attribute is defined as a dictionary with keys that describe its
        properties, such as "name", "type", "value_type", etc.

        Args:
            attributes (list[dict]): A list of attribute objects to create.
                Each attribute dictionary can include keys such as:
                {
                  "type": "base" | "category" | "certification" | "color" | "decor"
                    | "dimension" | "feature" | "material" | "optic" | "style"
                    | "usage",
                  "value_type": "boolean" | "number" | "string" | "list" | "range",
                  "value_unit": "cm" | "m" | "mm" | "inch",
                  "options": [
                    "string"
                  ],
                  "name_en": "string",
                  "name_de": "string",
                  "name_fr": "string",
                  "name_es": "string",
                  "name_it": "string",
                  "description_en": "string",
                  "description_de": "string",
                  "description_it": "string",
                  "description_es": "string",
                  "description_fr": "string",
                  "synonyms_en": [
                    "string"
                  ],
                  "synonyms_de": [
                    "string"
                  ],
                  "synonyms_fr": [
                    "string"
                  ],
                  "synonyms_es": [
                    "string"
                  ],
                  "synonyms_it": [
                    "string"
                  ],
                  "opposite_name_en": "string",
                  "opposite_name_de": "string",
                  "opposite_name_fr": "string",
                  "opposite_name_es": "string",
                  "opposite_name_it": "string",
                  "platforms": [
                    "new_architonic", "architonic", "archdaily", "daaily-index"
                  ],
                  "status": "online"
                }

        Raises:
            Exception: If the attribute creation process fails due to invalid input or
                other errors.

        Returns:
            Any: The result of the attribute creation process, which may include details
                of the newly created attributes.

        Example:
            ```python
            attributes_data = [
                {
                    "name": "Sample Attribute",
                    "type": "base",
                    "value_type": "boolean",
                    "value_unit": "cm",
                    "options": ["option1", "option2"],
                    "name_en": "Sample Attribute",
                    "name_de": "Beispielattribut",
                    "name_fr": "Attribut d'exemple",
                    "name_es": "Atributo de ejemplo",
                    "name_it": "Attributo di esempio",
                    "description_en": "A sample attribute",
                    "description_de": "Ein Beispielattribut",
                    "description_fr": "Un attribut d'exemple",
                    "description_es": "Un atributo de ejemplo",
                    "description_it": "Un attributo di esempio",
                    "synonyms_en": ["Example", "Sample"],
                    "synonyms_de": ["Beispiel"],
                    "synonyms_fr": ["Exemple"],
                    "synonyms_es": ["Ejemplo"],
                    "synonyms_it": ["Esempio"],
                    "opposite_name_en": "Opposite",
                    "opposite_name_de": "Gegenteil",
                    "opposite_name_fr": "Opposé",
                    "opposite_name_es": "Opuesto",
                    "opposite_name_it": "Opposto",
                    "platforms": ["new_architonic"],
                    "status": "online",
                    "revision_uuid": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
                }
            ]

            result = client.attributes.create(attributes=attributes_data)
            ```
        """
        return self._client.create_entities(
            EntityType.ATTRIBUTE, attributes, service=service
        )

    def create_one(self, attribute: dict, service: Service = Service.SPARKY):
        """
        Creates new attribute objects.

        This function allows for the creation of one or more new attributes in the
        system. Each attribute is defined as a dictionary with keys that describe its
        properties, such as "name", "type", "value_type", etc.

        Args:
            attribute (dict): A attribute object to create.
                Each attribute dictionary can include keys such as:
                {
                  "type": "base" | "category" | "certification" | "color" | "decor"
                    | "dimension" | "feature" | "material" | "optic" | "style"
                    | "usage",
                  "value_type": "boolean" | "number" | "string" | "list" | "range",
                  "value_unit": "cm" | "m" | "mm" | "inch",
                  "options": [
                    "string"
                  ],
                  "name_en": "string",
                  "name_de": "string",
                  "name_fr": "string",
                  "name_es": "string",
                  "name_it": "string",
                  "description_en": "string",
                  "description_de": "string",
                  "description_it": "string",
                  "description_es": "string",
                  "description_fr": "string",
                  "synonyms_en": [
                    "string"
                  ],
                  "synonyms_de": [
                    "string"
                  ],
                  "synonyms_fr": [
                    "string"
                  ],
                  "synonyms_es": [
                    "string"
                  ],
                  "synonyms_it": [
                    "string"
                  ],
                  "opposite_name_en": "string",
                  "opposite_name_de": "string",
                  "opposite_name_fr": "string",
                  "opposite_name_es": "string",
                  "opposite_name_it": "string",
                  "platforms": [
                    "new_architonic", "architonic", "archdaily", "daaily-index"
                  ],
                  "status": "online"
                }

        Raises:
            Exception: If the attribute creation process fails due to invalid input or
                other errors.

        Returns:
            Any: The result of the attribute creation process, which may include details
                of the newly created attributes.

        Example:
            ```python
            attributes_data = {
                    "name": "Sample Attribute",
                    "type": "base",
                    "value_type": "boolean",
                    "value_unit": "cm",
                    "options": ["option1", "option2"],
                    "name_en": "Sample Attribute",
                    "name_de": "Beispielattribut",
                    "name_fr": "Attribut d'exemple",
                    "name_es": "Atributo de ejemplo",
                    "name_it": "Attributo di esempio",
                    "description_en": "A sample attribute",
                    "description_de": "Ein Beispielattribut",
                    "description_fr": "Un attribut d'exemple",
                    "description_es": "Un atributo de ejemplo",
                    "description_it": "Un attributo di esempio",
                    "synonyms_en": ["Example", "Sample"],
                    "synonyms_de": ["Beispiel"],
                    "synonyms_fr": ["Exemple"],
                    "synonyms_es": ["Ejemplo"],
                    "synonyms_it": ["Esempio"],
                    "opposite_name_en": "Opposite",
                    "opposite_name_de": "Gegenteil",
                    "opposite_name_fr": "Opposé",
                    "opposite_name_es": "Opuesto",
                    "opposite_name_it": "Opposto",
                    "platforms": ["new_architonic"],
                    "status": "online",
                    "revision_uuid": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
                }

            result = client.attributes.create_one(attribute=attribute_data)
            ```
        """
        return self._client.create_entity(
            EntityType.ATTRIBUTE, attribute, service=service
        )

    def determine_attribute_value_type(
        self, value: Any
    ) -> tuple[Any, AttributeValueType]:
        return determine_attribute_value_type(value)

    def parse_attribute_value(self, value: Any) -> Any:
        parsed_value, _ = determine_attribute_value_type(value)
        return parsed_value

    def gen_new_attribute_object_with_extras(
        self,
        name_en: str,
        attribute_type: AttributeType,
        value_type: AttributeValueType,
        value_unit: AttributeValueUnit | None = None,
        **kwargs,
    ):
        return gen_new_attribute_object_with_extras(
            name_en, attribute_type, value_type, value_unit, **kwargs
        )
