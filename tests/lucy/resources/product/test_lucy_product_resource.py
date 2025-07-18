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
        result = client.products.add_or_update_image(
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

        result = client.products.add_or_update_image(
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
        result = client.products.add_or_update_image(
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

    def test_deter_score_up_to_date_no_product_data(self):
        """
        Test that an exception is raised if the product data is empty.
        """
        product_id = 1
        base_url = mock.sentinel.base_url
        credentials = mock.create_autospec(
            daaily.credentials.Credentials, instance=True
        )
        client = daaily.lucy.client.Client(credentials=credentials, base_url=base_url)
        # Simulate empty product data.
        client.get_entity = mock.MagicMock(return_value=DummyResponse({}, status=200))
        client.get_entity_audits = mock.MagicMock()
        try:
            client.products.deter_score_up_to_date(product_id)
            raise AssertionError("Expected an exception due to empty product data")
        except Exception as exc:
            assert str(exc) == "Could not deserialize product"

    def test_deter_score_up_to_date_no_scored_fields(self):
        """
        Test that an exception is raised if scored_fields or updated_at is missing in
        product data.
        """
        product_id = 2
        # Missing both scored_fields and updated_at in the nested dict.
        product_data = {"product_score": {}}
        base_url = mock.sentinel.base_url
        credentials = mock.create_autospec(
            daaily.credentials.Credentials, instance=True
        )
        client = daaily.lucy.client.Client(credentials=credentials, base_url=base_url)
        client.get_entity = mock.MagicMock(
            return_value=DummyResponse(product_data, status=200)
        )
        client.get_entity_audits = mock.MagicMock()
        try:
            client.products.deter_score_up_to_date(product_id)
            raise AssertionError(
                "Expected an exception due to missing scored fields or updated_at"
            )
        except Exception as exc:
            assert str(exc) == "Could not find scored fields in product score data"

    def test_deter_score_up_to_date_no_product_score_audits(self):
        """
        Test that if there are no product score audits the function returns True.
        """
        product_id = 3
        scored_fields = ["field1", "field2"]
        # Include updated_at along with scored_fields.
        product_data = {
            "product_score": {
                "scored_fields": scored_fields,
                "updated_at": "2025-01-01T00:00:00.000000",
            }
        }
        base_url = mock.sentinel.base_url
        credentials = mock.create_autospec(
            daaily.credentials.Credentials, instance=True
        )
        client = daaily.lucy.client.Client(credentials=credentials, base_url=base_url)
        client.get_entity = mock.MagicMock(
            return_value=DummyResponse(product_data, status=200)
        )
        # No audits exist for a product score update.
        client.get_entity_audits = mock.MagicMock(
            return_value=DummyResponse([], status=404)
        )
        result = client.products.deter_score_up_to_date(product_id)
        assert result is True

    def test_deter_score_up_to_date_audit_response_status_404(self):
        """
        Test that if the filtered audit call returns a 404 status,
        the function returns True.
        """
        product_id = 4
        scored_fields = ["field1", "field2"]
        # Include updated_at along with scored_fields.
        product_data = {
            "product_score": {
                "scored_fields": scored_fields,
                "updated_at": "2025-02-01T00:00:00.000000",
            }
        }
        base_url = mock.sentinel.base_url
        credentials = mock.create_autospec(
            daaily.credentials.Credentials, instance=True
        )
        client = daaily.lucy.client.Client(credentials=credentials, base_url=base_url)
        client.get_entity = mock.MagicMock(
            return_value=DummyResponse(product_data, status=200)
        )
        # Simulate a 404 response from the audit call.
        client.get_entity_audits = mock.MagicMock(
            return_value=DummyResponse([], status=404)
        )
        result = client.products.deter_score_up_to_date(product_id)
        assert result is True

    def test_deter_score_up_to_date_audit_exists(self):
        """
        Test that if a filtered audit exists (status not 404),
        the function returns False.
        """
        product_id = 5
        scored_fields = ["field1", "field2"]
        # Include updated_at along with scored_fields.
        product_data = {
            "product_score": {
                "scored_fields": scored_fields,
                "updated_at": "2025-03-01T00:00:00.000000",
            }
        }
        base_url = mock.sentinel.base_url
        credentials = mock.create_autospec(
            daaily.credentials.Credentials, instance=True
        )
        client = daaily.lucy.client.Client(credentials=credentials, base_url=base_url)
        client.get_entity = mock.MagicMock(
            return_value=DummyResponse(product_data, status=200)
        )
        # A normal audit response (status 200) indicates a matching change.
        client.get_entity_audits = mock.MagicMock(
            return_value=DummyResponse([{"dummy": "data"}], status=200)
        )
        result = client.products.deter_score_up_to_date(product_id)
        assert result is False

    def test_add_or_update_attributes_with_overwrite(self):
        """
        Test adding and updating product attributes with and without overwriting.
        """
        product_id = 101
        base_url = mock.sentinel.base_url
        credentials = mock.create_autospec(
            daaily.credentials.Credentials, instance=True
        )
        client = daaily.lucy.client.Client(credentials=credentials, base_url=base_url)

        existing_product_data = {
            "product_id": product_id,
            "attributes": [
                {
                    "name": "color_base",
                    "value": "red",
                    "source_actor": "internal_user",
                    "source_type": "unknown",
                },
                {
                    "name": "dimension_height",
                    "value": 300,
                    "source_actor": "ai",
                    "source_type": "html",
                },
                {  # this one should disappear
                    "name": "dimension_width",
                    "value": 250,
                    "source_actor": "ai",
                    "source_type": "html",
                },
            ],
        }

        expected_updated_product = {
            "product_id": product_id,
            "attributes": [
                {
                    "name": "color_base",
                    "value": "red",
                    "source_actor": "internal_user",
                    "source_type": "unknown",
                },
                {
                    "name": "dimension_height",
                    "value": 330,
                    "source_actor": "ai",
                    "source_type": "html",
                },
                {
                    "name": "material_frame",
                    "value": "metal",
                    "source_actor": "ai",
                    "source_type": "html",
                },
            ],
        }

        # Patch get_by_id and update_one
        client.products.get_by_id = mock.MagicMock(
            return_value=DummyResponse(existing_product_data)
        )

        # Capture the input to update_one
        def update_one_side_effect(product, service):
            assert product == expected_updated_product
            return DummyResponse(product, status=200)

        client.products.update_one = mock.MagicMock(side_effect=update_one_side_effect)

        # Attributes to add/update
        new_attributes = [
            {
                "name": "dimension_height",
                "value": 330,
                "source_actor": "ai",
                "source_type": "html",
            },
            {
                "name": "material_frame",
                "value": "metal",
                "source_actor": "ai",
                "source_type": "html",
            },
        ]

        result = client.products.add_or_update_attributes(
            product_id=product_id, attributes=new_attributes, overwrite_existing=True
        )

        assert result == expected_updated_product
        client.products.get_by_id.assert_called_once_with(product_id)
        client.products.update_one.assert_called_once()

    def test_add_or_update_attributes_without_overwrite(self):
        """
        Test adding and updating product attributes with and without overwriting.
        """
        product_id = 101
        base_url = mock.sentinel.base_url
        credentials = mock.create_autospec(
            daaily.credentials.Credentials, instance=True
        )
        client = daaily.lucy.client.Client(credentials=credentials, base_url=base_url)

        existing_product_data = {
            "product_id": product_id,
            "attributes": [
                {
                    "name": "color_base",
                    "value": "red",
                    "source_actor": "internal_user",
                    "source_type": "unknown",
                },
                {
                    "name": "dimension_height",
                    "value": 300,
                    "source_actor": "ai",
                    "source_type": "html",
                },
                {
                    "name": "dimension_depth",
                    "value": 150,
                    "source_actor": "ai",
                    "source_type": "html",
                },
            ],
        }

        new_attributes = [
            {
                "name": "dimension_height",
                "value": 330,
                "source_actor": "ai",
                "source_type": "html",
            },
            {
                "name": "material_frame",
                "value": "metal",
                "source_actor": "ai",
                "source_type": "html",
            },
        ]

        updated_product_data = {
            "product_id": product_id,
            "attributes": [
                {
                    "name": "color_base",
                    "value": "red",
                    "source_actor": "internal_user",
                    "source_type": "unknown",
                },
                {
                    "name": "dimension_height",
                    "value": 330,
                    "source_actor": "ai",
                    "source_type": "html",
                },
                {
                    "name": "dimension_depth",
                    "value": 150,
                    "source_actor": "ai",
                    "source_type": "html",
                },
                {
                    "name": "material_frame",
                    "value": "metal",
                    "source_actor": "ai",
                    "source_type": "html",
                },
            ],
        }

        # Patch get_by_id and update_one
        client.products.get_by_id = mock.MagicMock(
            return_value=DummyResponse(existing_product_data)
        )

        def update_one_side_effect(product, service):
            assert product == updated_product_data
            return DummyResponse(product, status=200)

        client.products.update_one = mock.MagicMock(side_effect=update_one_side_effect)

        # Attributes to add/update

        result = client.products.add_or_update_attributes(
            product_id=product_id, attributes=new_attributes, overwrite_existing=False
        )

        assert result == updated_product_data
        client.products.get_by_id.assert_called_once_with(product_id)
        client.products.update_one.assert_called_once()

    def test_add_or_update_attributes_without_source_fields_set(self):
        """
        Test adding and updating product attributes with and without overwriting.
        """
        product_id = 101
        base_url = mock.sentinel.base_url
        credentials = mock.create_autospec(
            daaily.credentials.Credentials, instance=True
        )
        client = daaily.lucy.client.Client(credentials=credentials, base_url=base_url)

        existing_product_data = {
            "product_id": product_id,
            "attributes": [
                {
                    "name": "color_base",
                    "value": "red",
                    "source_actor": "internal_user",
                    "source_type": "unknown",
                },
                {
                    "name": "dimension_height",
                    "value": 300,
                    "source_actor": "ai",
                    "source_type": "html",
                },
            ],
        }

        new_attributes = [
            {  # should default to internal_user and unknown
                "name": "dimension_height",
                "value": 330,
            },
            {  # should default to internal_user and unknown
                "name": "material_frame",
                "value": "metal",
            },
        ]

        updated_product_data = {
            "product_id": product_id,
            "attributes": [
                {
                    "name": "dimension_height",
                    "value": 300,
                    "source_actor": "ai",
                    "source_type": "html",
                },
                {
                    "name": "dimension_height",
                    "value": 330,
                    "source_actor": "internal_user",
                    "source_type": "unknown",
                },
                {
                    "name": "material_frame",
                    "value": "metal",
                    "source_actor": "internal_user",
                    "source_type": "unknown",
                },
            ],
        }

        # Patch get_by_id and update_one
        client.products.get_by_id = mock.MagicMock(
            return_value=DummyResponse(existing_product_data)
        )

        def update_one_side_effect(product, service):
            assert product == updated_product_data
            return DummyResponse(product, status=200)

        client.products.update_one = mock.MagicMock(side_effect=update_one_side_effect)

        # Attributes to add/update

        result = client.products.add_or_update_attributes(
            product_id=product_id, attributes=new_attributes, overwrite_existing=True
        )

        assert result == updated_product_data
        client.products.get_by_id.assert_called_once_with(product_id)
        client.products.update_one.assert_called_once()

    def test_add_or_update_attributes_only_one_actor_with_overwrite(self):
        """
        Test adding and updating product attributes with and without overwriting.
        """
        product_id = 101
        base_url = mock.sentinel.base_url
        credentials = mock.create_autospec(
            daaily.credentials.Credentials, instance=True
        )
        client = daaily.lucy.client.Client(credentials=credentials, base_url=base_url)

        existing_product_data = {
            "product_id": product_id,
            "attributes": [
                {
                    "name": "color_base",
                    "value": "red",
                    "source_actor": "internal_user",
                    "source_type": "unknown",
                },
                {
                    "name": "dimension_width",
                    "value": 440,
                    "source_actor": "ai",
                    "source_type": "html",
                },
            ],
        }

        # Attributes to add/update
        new_attributes = [
            {
                "name": "dimension_height",
                "value": 330,
                "source_actor": "internal_user",
                "source_type": "unknown",
            },
            {
                "name": "material_frame",
                "value": "metal",
                "source_actor": "internal_user",
                "source_type": "unknown",
            },
        ]

        updated_product_data = {
            "product_id": product_id,
            "attributes": [
                {
                    "name": "dimension_width",
                    "value": 440,
                    "source_actor": "ai",
                    "source_type": "html",
                },
                {
                    "name": "dimension_height",
                    "value": 330,
                    "source_actor": "internal_user",
                    "source_type": "unknown",
                },
                {
                    "name": "material_frame",
                    "value": "metal",
                    "source_actor": "internal_user",
                    "source_type": "unknown",
                },
            ],
        }

        # Patch get_by_id and update_one
        client.products.get_by_id = mock.MagicMock(
            return_value=DummyResponse(existing_product_data)
        )

        def update_one_side_effect(product, service):
            assert product == updated_product_data
            return DummyResponse(product, status=200)

        client.products.update_one = mock.MagicMock(side_effect=update_one_side_effect)

        result = client.products.add_or_update_attributes(
            product_id=product_id, attributes=new_attributes, overwrite_existing=True
        )

        assert result == updated_product_data
        client.products.get_by_id.assert_called_once_with(product_id)
        client.products.update_one.assert_called_once()
