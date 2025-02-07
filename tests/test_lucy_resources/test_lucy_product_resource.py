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


class TestDeterOwnershipOfFields:
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
                        "old_value": "3D Floorlamp Alu",
                        "new_value": "3D Floorlamp Alu ",
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
            "name_de": "3D Floorlamp Alu ",
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
