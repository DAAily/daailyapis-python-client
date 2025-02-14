import unittest.mock as mock

import daaily.credentials
import daaily.credentials_sally
import daaily.lucy.client
import daaily.lucy.utils
import daaily.transport.urllib3_http


class CredentialsStub(daaily.credentials_sally.Credentials):
    def __init__(self, id_token="token"):
        self.id_token = id_token

    def apply(self, headers, id_token=None):
        headers["authorization"] = self.id_token

    def before_request(self, request, headers):
        self.apply(headers)


class DummyResponse:
    """
    A dummy response to simulate responses from get_entity_audits and get_entity.
    """

    def __init__(self, data, status=200, headers=None):
        self._data = data
        self.status = status
        self.headers = headers or {}

    def json(self):
        return self._data


class Filter:
    def __init__(self, key, value):
        self.key = key
        self.value = value


class EntityType:
    PRODUCT = "product"


class TestProductResource:
    def test_audit_list_diff_from_user(self):
        """
        When an audit entry exists for a list field (e.g., "cads") and the owner made
        the change, the method returns only the new items (i.e. those not in the old
        list).
        """
        owner_email = "owner@example.com"
        product_id = 101
        changed_fields = ["cads"]
        audits = [
            {
                "changed_by": owner_email,
                "changed_at": "2025-02-07T14:04:03.009000",
                "entity_id": 101,
                "changes": {
                    "cads": {
                        "new_value": [{"id": 1, "name": "A"}, {"id": 2, "name": "B"}],
                        "old_value": [{"id": 1, "name": "A"}],
                    }
                },
            }
        ]
        product_data = {"created_by": "someone_else", "cads": []}
        base_url = mock.sentinel.base_url
        credentials = mock.create_autospec(
            daaily.credentials.Credentials, instance=True
        )
        client = daaily.lucy.client.Client(credentials=credentials, base_url=base_url)
        client.get_entity_audits = mock.MagicMock(return_value=DummyResponse(audits))
        client.get_entity = mock.MagicMock(return_value=DummyResponse(product_data))

        result = client.products.deter_ownership_of_fields(
            product_id, changed_fields, owner_email
        )
        expected = {"cads": [{"id": 2, "name": "B"}]}
        assert result == expected

    def test_audit_list_diff_from_other_user(self):
        """
        When an audit entry exists for a list field (e.g., "cads") and the owner made
        the change, the method returns only the new items (i.e. those not in the old
        list).
        """
        other_user_email = "other-user@example.com"
        owner_email = "owner@example.com"
        product_id = 101
        changed_fields = ["cads", "name_en", "name_de"]
        audits = [
            {
                "changed_by": owner_email,
                "changed_at": "2025-02-08T14:04:03.009000",
                "entity_id": 101,
                "changes": {
                    "cads": {
                        "new_value": [
                            {"id": 1, "name": "A"},
                            {"id": 2, "name": "B"},
                            {"id": 3, "name": "C"},
                        ],
                        "old_value": [{"id": 1, "name": "A"}, {"id": 2, "name": "B"}],
                    },
                    "name_en": {
                        "new_value": "Product Name",
                        "old_value": "Old Product Name",
                    },
                },
            },
            {
                "changed_by": other_user_email,
                "changed_at": "2025-02-07T14:04:03.009000",
                "entity_id": 101,
                "changes": {
                    "cads": {
                        "new_value": [{"id": 1, "name": "A"}, {"id": 2, "name": "B"}],
                        "old_value": [{"id": 1, "name": "A"}],
                    },
                    "name_de": {
                        "new_value": "Produkt Name",
                        "old_value": "Old Product",
                    },
                },
            },
        ]
        product_data = {"created_by": "someone_else", "cads": []}
        base_url = mock.sentinel.base_url
        credentials = mock.create_autospec(
            daaily.credentials.Credentials, instance=True
        )
        client = daaily.lucy.client.Client(credentials=credentials, base_url=base_url)
        client.get_entity_audits = mock.MagicMock(return_value=DummyResponse(audits))
        client.get_entity = mock.MagicMock(return_value=DummyResponse(product_data))
        result = client.products.deter_ownership_of_fields(
            product_id, changed_fields, owner_email
        )
        expected = {"cads": [{"id": 3, "name": "C"}], "name_en": "Product Name"}
        assert result == expected

    def test_audit_creator_matches(self):
        """
        If no audit entry exists but the product was created by the owner,
        then the method returns the product fields.
        """
        owner_email = "owner@example.com"
        product_id = 202
        changed_fields = ["name_en", "live_link"]
        audits = [
            {
                "changed_by": owner_email,
                "changed_at": "2025-02-07T14:04:03.009000",
                "entity_id": 202,
                "changes": {
                    "cads": {
                        "new_value": [
                            {"id": 1, "name": "A"},
                            {"id": 2, "name": "B"},
                            {"id": 3, "name": "C"},
                        ],
                        "old_value": [{"id": 1, "name": "A"}, {"id": 2, "name": "B"}],
                    },
                    "live_link": {
                        "new_value": {"url": "http://example.com", "is_enabled": True},
                        "old_value": {
                            "url": "http://old.example.com",
                            "is_enabled": False,
                        },
                    },
                    "name_en": {
                        "new_value": "Product Name",
                        "old_value": "Old Product Name",
                    },
                },
            },
        ]
        product_data = {
            "created_by": owner_email,
            "name_en": "Product Name Irrelevant",
            "live_link": {"url": "http://example-irrelevant.com", "is_enabled": False},
        }
        base_url = mock.sentinel.base_url
        credentials = mock.create_autospec(
            daaily.credentials.Credentials, instance=True
        )
        client = daaily.lucy.client.Client(credentials=credentials, base_url=base_url)
        client.get_entity_audits = mock.MagicMock(return_value=DummyResponse(audits))
        client.get_entity = mock.MagicMock(return_value=DummyResponse(product_data))
        result = client.products.deter_ownership_of_fields(
            product_id, changed_fields, owner_email
        )
        expected = {
            "name_en": "Product Name",
            "live_link": {"url": "http://example.com", "is_enabled": True},
        }
        assert result == expected

    def test_no_audit_creator_matches(self):
        """
        If no audit entry exists but the product was created by the owner,
        then the method returns the product fields.
        """
        owner_email = "owner@example.com"
        product_id = 202
        changed_fields = ["name_en", "live_link"]

        audits = []  # No audits available.
        product_data = {
            "created_by": owner_email,
            "live_link": {"url": "http://example.com", "is_enabled": True},
            "name_en": "Product Name",
        }
        base_url = mock.sentinel.base_url
        credentials = mock.create_autospec(
            daaily.credentials.Credentials, instance=True
        )
        client = daaily.lucy.client.Client(credentials=credentials, base_url=base_url)
        client.get_entity_audits = mock.MagicMock(return_value=DummyResponse(audits))
        client.get_entity = mock.MagicMock(return_value=DummyResponse(product_data))
        result = client.products.deter_ownership_of_fields(
            product_id, changed_fields, owner_email
        )
        expected = {
            "name_en": "Product Name",
            "live_link": {"url": "http://example.com", "is_enabled": True},
        }
        assert result == expected

    def test_no_audit_creator_not_matches(self):
        """
        If no audit entry exists and the product creator does not match the owner,
        the method should return None.
        """
        owner_email = "owner@example.com"
        product_id = 303
        changed_fields = ["name_en", "live_link"]
        audits = []  # No audits available.
        product_data = {
            "created_by": "other@example.com",
            "name_en": "Product Name",
            "live_link": {"url": "http://example.com", "is_enabled": True},
        }
        base_url = mock.sentinel.base_url
        credentials = mock.create_autospec(
            daaily.credentials.Credentials, instance=True
        )
        client = daaily.lucy.client.Client(credentials=credentials, base_url=base_url)
        client.get_entity_audits = mock.MagicMock(return_value=DummyResponse(audits))
        client.get_entity = mock.MagicMock(return_value=DummyResponse(product_data))
        result = client.products.deter_ownership_of_fields(
            product_id, changed_fields, owner_email
        )
        assert result is None

    def test_single_audit_by_owner(self):
        """
        If no audit entry exists and the product creator does not match the owner,
        the method should return None.
        """
        owner_email = "owner@example.com"
        product_id = 303
        changed_fields = ["name_en", "name_de", "live_link"]
        audits = [
            {
                "entity_id": 303,
                "changed_at": "2025-02-07T14:04:03.009000",
                "changed_by": owner_email,
                "changes": {
                    "name_de": {
                        "old_value": "3D Floor lamp Alu",
                        "new_value": "3D Floor lamp Alu ",
                    }
                },
            }
        ]
        product_data = {
            "created_by": "other@example.com",
            "name_en": "Product Name",
            "name_de": "Should not be used",
            "live_link": {"url": "http://example.com", "is_enabled": True},
        }
        base_url = mock.sentinel.base_url
        credentials = mock.create_autospec(
            daaily.credentials.Credentials, instance=True
        )
        client = daaily.lucy.client.Client(credentials=credentials, base_url=base_url)
        client.get_entity_audits = mock.MagicMock(return_value=DummyResponse(audits))
        client.get_entity = mock.MagicMock(return_value=DummyResponse(product_data))
        result = client.products.deter_ownership_of_fields(
            product_id, changed_fields, owner_email
        )
        expected = {
            "name_de": "3D Floor lamp Alu ",
        }
        assert result == expected

    def test_audit_list_diff_from_other_user_after(self):
        other_user_email = "other-user@example.com"
        owner_email = "owner2@example.com"
        product_id = 101
        changed_fields = ["cads", "name_en", "name_de"]
        audits = [
            {
                "entity_id": 101,
                "changed_by": other_user_email,
                "changed_at": "2025-02-08T14:04:03.009000",
                "changes": {
                    "cads": {
                        "new_value": [
                            {"id": 1, "name": "A"},
                            {"id": 2, "name": "B"},
                            {"id": 3, "name": "C"},
                        ],
                        "old_value": [{"id": 1, "name": "A"}, {"id": 2, "name": "B"}],
                    },
                    "name_en": {
                        "new_value": "Product Name",
                        "old_value": "Old Product Name",
                    },
                },
            },
            {
                "entity_id": 101,
                "changed_by": owner_email,
                "changed_at": "2025-02-07T14:04:03.009000",
                "changes": {
                    "cads": {
                        "new_value": [{"id": 1, "name": "A"}, {"id": 2, "name": "B"}],
                        "old_value": [{"id": 1, "name": "A"}],
                    },
                },
            },
        ]
        # The fallback product data (should not be used in this scenario).
        product_data = {"created_by": "someone_else", "cads": []}
        base_url = mock.sentinel.base_url
        credentials = mock.create_autospec(
            daaily.credentials.Credentials, instance=True
        )
        client = daaily.lucy.client.Client(credentials=credentials, base_url=base_url)
        client.get_entity_audits = mock.MagicMock(return_value=DummyResponse(audits))
        client.get_entity = mock.MagicMock(return_value=DummyResponse(product_data))

        result = client.products.deter_ownership_of_fields(
            product_id, changed_fields, owner_email
        )
        assert result is None

    def test_audit_list_diff_from_same_user_after(self):
        owner_email = "owner@example.com"
        product_id = 101
        changed_fields = ["cads", "name_en", "name_de"]
        audits = [
            {
                "entity_id": 101,
                "changed_by": owner_email,
                "changed_at": "2025-02-08T14:04:03.009000",
                "changes": {
                    "cads": {
                        "new_value": [
                            {"id": 1, "name": "A"},
                            {"id": 2, "name": "B"},
                            {"id": 3, "name": "C"},
                        ],
                        "old_value": [{"id": 1, "name": "A"}, {"id": 2, "name": "B"}],
                    },
                    "name_en": {
                        "new_value": "Product Name",
                        "old_value": "Old Product Name",
                    },
                },
            },
            {
                "entity_id": 101,
                "changed_by": owner_email,
                "changed_at": "2025-02-07T14:04:03.009000",
                "changes": {
                    "cads": {
                        "new_value": [{"id": 1, "name": "A"}, {"id": 2, "name": "B"}],
                        "old_value": [{"id": 1, "name": "A"}],
                    },
                },
            },
        ]
        # The fallback product data (should not be used in this scenario).
        product_data = {"created_by": "someone_else", "cads": []}
        base_url = mock.sentinel.base_url
        credentials = mock.create_autospec(
            daaily.credentials.Credentials, instance=True
        )
        client = daaily.lucy.client.Client(credentials=credentials, base_url=base_url)
        client.get_entity_audits = mock.MagicMock(return_value=DummyResponse(audits))
        client.get_entity = mock.MagicMock(return_value=DummyResponse(product_data))
        result = client.products.deter_ownership_of_fields(
            product_id, changed_fields, owner_email
        )
        expected = {"cads": [{"id": 3, "name": "C"}], "name_en": "Product Name"}
        assert result == expected

    def test_add_new_product_image(self):
        """
        Test adding a new product image.
        """
        product_id = 12345
        image_path = "/path/to/image.jpg"
        image_data = {
            "image_usages": ["pro-g"],
            "image_type": "Cut-out image",
            "list_order": 1,
            "direct_link": {"url": "https://example.com/image.jpg"},
            "description": "A sample product image",
        }
        initial_product_data = {
            "id": product_id,
            "name": "Sample Product",
            "images": None,
        }
        final_product_data = {
            "id": product_id,
            "name": "Sample Product",
            "images": [
                {
                    "blob_id": f"m-on/123345/p/{product_id}/seat_e1be67b1.jpeg/17393",
                    "image_usages": ["pro-g"],
                    "image_type": "Cut-out image",
                    "list_order": 1,
                    "direct_link": {"url": "https://example.com/image.jpg"},
                    "width": 1100,
                    "size": 87335,
                    "file_type": "image/jpeg",
                }
            ],
        }
        base_url = mock.sentinel.base_url
        credentials = mock.create_autospec(
            daaily.credentials.Credentials, instance=True
        )
        client = daaily.lucy.client.Client(credentials=credentials, base_url=base_url)
        client.get_entity = mock.MagicMock(
            return_value=DummyResponse(initial_product_data)
        )
        client.products.upload_image = mock.MagicMock(
            return_value={
                "image_blob_id": f"m-on/123345/p/{product_id}/seat_e1be67b1.jpeg/17393",
                "image_mime_type": "image/jpeg",
                "image_height": 412,
                "image_width": 1100,
                "image_size": 87335,
            }
        )
        client.update_entity = mock.MagicMock(
            return_value=DummyResponse(final_product_data)
        )

        def update_side_effect(entity_type, product):
            assert entity_type == EntityType.PRODUCT
            assert product["images"][0] == {
                "blob_id": f"m-on/123345/p/{product_id}/seat_e1be67b1.jpeg/17393",
                "image_usages": ["pro-g"],
                "image_type": "Cut-out image",
                "list_order": 1,
                "direct_link": {"url": "https://example.com/image.jpg"},
                "description": "A sample product image",
                "file_type": "image/jpeg",
                "height": 412,
                "width": 1100,
                "size": 87335,
            }
            return DummyResponse(final_product_data)

        client.update_entity.side_effect = update_side_effect
        result = client.products.add_or_update_product_image(
            product_id=product_id, image_path=image_path, **image_data
        )
        assert result.json() == final_product_data
        client.products.upload_image.assert_called_once_with(
            product_id=product_id,
            image_path=image_path,
            image_bytes=None,
            mime_type=None,
            filename=None,
            old_blob_id=None,
            **image_data,
        )
        client.update_entity.assert_called_once()

    def test_update_existing_product_image(self):
        """
        Test updating an existing product image.
        """
        product_id = 12345
        old_blob_id = "existing-blob-id"
        image_data = {
            "blob_id": old_blob_id,
            "image_usages": ["pro-g"],
            "image_type": "Cut-out image",
            "list_order": 2,
            "direct_link": {"url": "https://example.com/image.jpg"},
            "description": "A sample product image",
        }
        initial_product_data = {
            "id": product_id,
            "name": "Sample Product",
            "images": [
                {
                    "blob_id": old_blob_id,
                    "image_usages": ["pro-b"],
                    "image_type": "Cut-out image",
                    "list_order": 1,
                    "direct_link": {"url": "https://example.com/image.jpg"},
                    "description": "A sample product image",
                }
            ],
        }
        final_product_data = {
            "id": product_id,
            "name": "Sample Product",
            "images": [
                {
                    "blob_id": old_blob_id,
                    "image_usages": ["pro-g"],
                    "image_type": "Cut-out image",
                    "list_order": 2,
                    "direct_link": {"url": "https://example.com/image.jpg"},
                    "description": "A sample product image",
                }
            ],
        }
        base_url = mock.sentinel.base_url
        credentials = mock.create_autospec(
            daaily.credentials.Credentials, instance=True
        )
        client = daaily.lucy.client.Client(credentials=credentials, base_url=base_url)
        client.get_entity = mock.MagicMock(
            return_value=DummyResponse(initial_product_data)
        )
        client.update_entity = mock.MagicMock(
            return_value=DummyResponse(final_product_data)
        )
        client.products.upload_image = mock.MagicMock(
            return_value={
                "image_blob_id": f"m-on/123345/p/{product_id}/seat_e1be67b1.jpeg/17393",
                "image_mime_type": "image/jpeg",
                "image_height": 412,
                "image_width": 1100,
                "image_size": 87335,
            }
        )

        # Capture the product data before the update call
        def update_side_effect(entity_type, product):
            assert entity_type == EntityType.PRODUCT
            assert product["images"][0] == {
                "blob_id": old_blob_id,
                "image_usages": ["pro-g"],
                "image_type": "Cut-out image",
                "list_order": 2,
                "direct_link": {"url": "https://example.com/image.jpg"},
                "description": "A sample product image",
            }
            return DummyResponse(final_product_data)

        client.update_entity.side_effect = update_side_effect

        result = client.products.add_or_update_product_image(
            product_id=product_id, old_blob_id=old_blob_id, **image_data
        )
        assert result.json() == final_product_data
        client.products.upload_image.assert_not_called()
        client.update_entity.assert_called_once()

    def test_update_existing_product_image_with_new_image_path(self):
        """
        Test updating an existing product image with a new image path.
        """
        product_id = 12345
        old_blob_id = "existing-blob-id"
        new_image_path = "/path/to/new_image.jpg"
        image_data = {
            "blob_id": old_blob_id,
            "image_usages": ["pro-g"],
            "image_type": "Cut-out image",
            "list_order": 2,
            "direct_link": {"url": "https://example.com/image.jpg"},
            "description": "A sample product image",
        }
        initial_product_data = {
            "id": product_id,
            "name": "Sample Product",
            "images": [
                {
                    "blob_id": old_blob_id,
                    "image_usages": ["pro-b"],
                    "image_type": "Cut-out image",
                    "list_order": 1,
                    "direct_link": {"url": "https://example.com/image.jpg"},
                    "description": "A sample product image",
                }
            ],
        }
        final_product_data = {
            "id": product_id,
            "name": "Sample Product",
            "images": [
                {
                    "blob_id": f"m-on/123345/p/{product_id}/seat_e1be67b1.jpeg/17393",
                    "image_usages": ["pro-g"],
                    "image_type": "Cut-out image",
                    "file_type": "image/jpeg",
                    "list_order": 2,
                    "direct_link": {"url": "https://example.com/image.jpg"},
                    "description": "A sample product image",
                    "height": 412,
                    "width": 1100,
                    "size": 87335,
                }
            ],
        }
        base_url = mock.sentinel.base_url
        credentials = mock.create_autospec(
            daaily.credentials.Credentials, instance=True
        )
        client = daaily.lucy.client.Client(credentials=credentials, base_url=base_url)
        client.get_entity = mock.MagicMock(
            return_value=DummyResponse(initial_product_data)
        )
        client.update_entity = mock.MagicMock(
            return_value=DummyResponse(final_product_data)
        )
        client.products.upload_image = mock.MagicMock(
            return_value={
                "image_blob_id": f"m-on/123345/p/{product_id}/seat_e1be67b1.jpeg/17393",
                "image_mime_type": "image/jpeg",
                "image_height": 412,
                "image_width": 1100,
                "image_size": 87335,
            }
        )

        # Capture the product data before the update call
        def update_side_effect(entity_type, product):
            assert entity_type == EntityType.PRODUCT
            assert product["images"][0] == {
                "blob_id": f"m-on/123345/p/{product_id}/seat_e1be67b1.jpeg/17393",
                "image_usages": ["pro-g"],
                "image_type": "Cut-out image",
                "file_type": "image/jpeg",
                "list_order": 2,
                "direct_link": {"url": "https://example.com/image.jpg"},
                "description": "A sample product image",
                "height": 412,
                "width": 1100,
                "size": 87335,
            }

            return DummyResponse(final_product_data)

        client.update_entity.side_effect = update_side_effect
        result = client.products.add_or_update_product_image(
            product_id=product_id,
            image_path=new_image_path,
            old_blob_id=old_blob_id,
            **image_data,
        )
        assert result.json() == final_product_data
        client.products.upload_image.assert_called_once_with(
            product_id=product_id,
            image_path=new_image_path,
            image_bytes=None,
            mime_type=None,
            filename=None,
            old_blob_id=old_blob_id,
            **image_data,
        )
        client.update_entity.assert_called_once()
