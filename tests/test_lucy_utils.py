import pytest

import daaily.lucy.utils


class TestLucyUtils:
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
