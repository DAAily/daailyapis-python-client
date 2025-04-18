import json
import unittest

import pytest

import daaily.lucy.utils


class TestLucyUtils(unittest.TestCase):
    def test_constructor(self):
        pass

    def test_lucy_utils_add_image_to_product(self):
        image_added_to_product_1 = daaily.lucy.utils.add_image_to_product(
            {"product_id": 234243, "images": None}, {"blob_id": "blob_id_string"}
        )
        assert image_added_to_product_1 == {
            "product_id": 234243,
            "images": [{"blob_id": "blob_id_string"}],
        }
        image_added_to_product_2 = daaily.lucy.utils.add_image_to_product(
            {"product_id": 234243, "images": []}, {"blob_id": "blob_id_string"}
        )
        assert image_added_to_product_2 == {
            "product_id": 234243,
            "images": [{"blob_id": "blob_id_string"}],
        }
        image_added_to_product_3 = daaily.lucy.utils.add_image_to_product(
            {"product_id": 234243, "images": [{"blob_id": "blob_id_string"}]},
            {"blob_id": "blob_id_string_2"},
        )
        assert image_added_to_product_3 == {
            "product_id": 234243,
            "images": [{"blob_id": "blob_id_string"}, {"blob_id": "blob_id_string_2"}],
        }

    def test_gen_new_image_object_with_extras(self):
        new_image_object = daaily.lucy.utils.gen_new_image_object_with_extras(
            "blob_id_string", image_usages=["pro-g"], extra_key="extra_value"
        )
        assert new_image_object == {
            "blob_id": "blob_id_string",
            "image_usages": ["pro-g"],
            "extra_key": "extra_value",
        }

    def test_add_image_to_product_by_blob_id(self):
        product = {"product_id": 234243, "images": [{"blob_id": "blob_id_string"}]}
        image = {"blob_id": "blob_id_string", "extra_key": "extra_value"}

        updated_product = daaily.lucy.utils.add_image_to_product_by_blob_id(
            product, image
        )
        assert updated_product == {
            "product_id": 234243,
            "images": [{"blob_id": "blob_id_string", "extra_key": "extra_value"}],
        }

        new_image = {"blob_id": "blob_id_string_2", "extra_key": "extra_value_2"}
        updated_product = daaily.lucy.utils.add_image_to_product_by_blob_id(
            product, new_image
        )
        assert updated_product == {
            "product_id": 234243,
            "images": [
                {"blob_id": "blob_id_string", "extra_key": "extra_value"},
                {"blob_id": "blob_id_string_2", "extra_key": "extra_value_2"},
            ],
        }

        with pytest.raises(ValueError):
            daaily.lucy.utils.add_image_to_product_by_blob_id(
                product, {"extra_key": "missing_blob_id"}
            )

    def test_extract_extension_from_blob_id(self):
        assert (
            daaily.lucy.utils.extract_extension_from_blob_id(
                "path/to/file.jpg/3242432234234"
            )
            == "jpg"
        )
        assert (
            daaily.lucy.utils.extract_extension_from_blob_id(
                "path/to/file.tar.gz/3242432234234"
            )
            == "gz"
        )
        assert (
            daaily.lucy.utils.extract_extension_from_blob_id("file.txt/3242432234234")
            == "txt"
        )

    def test_extract_mime_type_from_extension(self):
        assert daaily.lucy.utils.extract_mime_type_from_extension("jpg") == "image/jpeg"
        assert daaily.lucy.utils.extract_mime_type_from_extension("png") == "image/png"
        assert daaily.lucy.utils.extract_mime_type_from_extension("unknown") is None

    def test_valid_message(self):
        binary_data = json.dumps(
            {
                "title": "Duplicate key found",
                "description": json.dumps(
                    {
                        "index": 0,
                        "code": 11000,
                        "errmsg": "E11000 duplicate key error collection: "
                        + "lucy-dev.attributes index: attribute_id_1 dup key: "
                        + "{ attribute_id: 1024 }",
                        "keyPattern": {"name": 1},
                        "keyValue": {"name": "feature_backrest_fixed"},
                    }
                ),
                "identifier_field": None,
                "identifier": None,
            }
        ).encode("utf-8")
        (
            key_pattern,
            dup_value,
        ) = daaily.lucy.utils.deter_duplicate_key_from_error_message(binary_data)
        self.assertEqual((key_pattern, dup_value), ("name", "feature_backrest_fixed"))

    def test_python_style_dict_message(self):
        """
        In this scenario, 'description' is a Python-style dict string
        (single quotes, etc.) rather than strict JSON.
        """
        # 1) Build the Python dict whose "errmsg" has the 'index: name_1 dup key..' text
        description_py_dict = {
            "index": 0,
            "code": 11000,
            "errmsg": (
                "E11000 duplicate key error collection: lucy-staging.attributes "
                'index: name_1 dup key: { name: "material_" }'
            ),
            "keyPattern": {"name": 1},
            "keyValue": {"name": "material_"},
        }
        # 2) Use repr(...) to create a Python‐style string from that dict,
        #    then JSON‐dump the entire top‐level object so that it is valid JSON.
        payload = {
            "title": "Duplicate key found",
            "description": repr(description_py_dict),
            "identifier_field": None,
            "identifier": None,
        }
        binary_data = json.dumps(payload).encode("utf-8")
        (
            index_name,
            dup_value,
        ) = daaily.lucy.utils.deter_duplicate_key_from_error_message(binary_data)
        self.assertEqual((index_name, dup_value), ("name", "material_"))

    def test_missing_dup_key(self):
        binary_data = (
            b'{"title": "Duplicate key found", "description": "{\'index\': 0, '
            b"'code': 11000, 'errmsg': 'E11000 error without duplicate key "
            b'info\', "identifier_field": null, "identifier": null}'
        )
        result = daaily.lucy.utils.deter_duplicate_key_from_error_message(binary_data)
        self.assertIsNone(result[0])
        self.assertIsNone(result[1])

    def test_malformed_json(self):
        binary_data = b"not a valid json"
        result = daaily.lucy.utils.deter_duplicate_key_from_error_message(binary_data)
        self.assertIsNone(result[0])
        self.assertIsNone(result[1])
