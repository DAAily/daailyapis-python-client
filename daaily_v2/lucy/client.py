from daaily_v2.enums import Environment
from daaily_v2.http.client import Client as HttpClient
from daaily_v2.http.utility import add_authorization_header
from daaily_v2.lucy.enums import Currency, LucyEndpoint, Status
from daaily_v2.lucy.utility import (
    extract_response_data,
    gen_request_url_with_id,
    gen_request_url_with_params,
    get_collection_params,
    get_creator_params,
    get_distributor_params,
    get_fair_params,
    get_family_params,
    get_filter_params,
    get_group_params,
    get_journalist_params,
    get_lucy_v2_endpoint_url,
    get_manufacturer_params,
    get_product_params,
    get_project_params,
    get_story_params,
)
from daaily_v2.sally.client import Client as SallyClient


class Client:
    def __init__(self, environment: Environment = Environment.STAGING) -> None:
        self.sally_client = SallyClient()
        self.http_client = HttpClient()
        self.environment = environment

    def _get_request_headers(self) -> dict:
        sally_id_token = self.sally_client.get_token()
        headers = add_authorization_header(sally_id_token, None)
        return headers

    def _get_entity(self, lucy_endpoint: LucyEndpoint, entity_id: int) -> dict:
        get_endpoint_url = get_lucy_v2_endpoint_url(self.environment, lucy_endpoint)
        request_url = gen_request_url_with_id(get_endpoint_url, entity_id)
        headers = self._get_request_headers()
        response = self.http_client.get_request(request_url, headers)
        return extract_response_data(response)

    def _get_entities(self, lucy_endpoint: LucyEndpoint, params: dict) -> list[dict]:
        get_endpoint_url = get_lucy_v2_endpoint_url(self.environment, lucy_endpoint)
        request_url = gen_request_url_with_params(get_endpoint_url, params)
        headers = self._get_request_headers()
        response = self.http_client.get_request(request_url, headers)
        return extract_response_data(response)

    # PUBLIC

    # GET SINGLE

    def get_manufacturer(self, manufacturer_id: int) -> dict:
        return self._get_entity(LucyEndpoint.MANUFACTURER, manufacturer_id)

    def get_distributor(self, distributor_id: int) -> dict:
        return self._get_entity(LucyEndpoint.DISTRIBUTOR, distributor_id)

    def get_collection(self, collection_id: int) -> dict:
        return self._get_entity(LucyEndpoint.COLLECTION, collection_id)

    def get_journalist(self, journalist_id: int) -> dict:
        return self._get_entity(LucyEndpoint.JOURNALIST, journalist_id)

    def get_project(self, project_id: int) -> dict:
        return self._get_entity(LucyEndpoint.PROJECT, project_id)

    def get_product(self, product_id: int) -> dict:
        return self._get_entity(LucyEndpoint.PRODUCT, product_id)

    def get_family(self, family_id: int) -> dict:
        return self._get_entity(LucyEndpoint.FAMILY, family_id)

    def get_creator(self, creator_id: int) -> dict:
        return self._get_entity(LucyEndpoint.CREATOR, creator_id)

    def get_filter(self, filter_id: int) -> dict:
        return self._get_entity(LucyEndpoint.FILTER, filter_id)

    def get_story(self, story_id: int) -> dict:
        return self._get_entity(LucyEndpoint.STORY, story_id)

    def get_group(self, group_id: int) -> dict:
        return self._get_entity(LucyEndpoint.GROUP, group_id)

    def get_fair(self, fair_id: int) -> dict:
        return self._get_entity(LucyEndpoint.FAIR, fair_id)

    # GET MULTIPLE

    def get_manufacturers(
        self,
        manufacturer_ids: list[int] | None = None,
        manufacturer_name: str | None = None,
        skip: int = 0,
        limit: int = 500,
    ) -> list[dict]:
        params = get_manufacturer_params(
            skip, limit, manufacturer_ids, manufacturer_name
        )
        return self._get_entities(LucyEndpoint.MANUFACTURER, params)

    def get_distributors(
        self,
        distributor_ids: list[int] | None = None,
        distributor_name: str | None = None,
        skip: int = 0,
        limit: int = 500,
    ) -> list[dict]:
        params = get_distributor_params(skip, limit, distributor_ids, distributor_name)
        return self._get_entities(LucyEndpoint.DISTRIBUTOR, params)

    def get_collections(
        self,
        manufacturer_id: int | None = None,
        collection_ids: list[int] | None = None,
        skip: int = 0,
        limit: int = 500,
    ) -> list[dict]:
        params = get_collection_params(skip, limit, manufacturer_id, collection_ids)
        return self._get_entities(LucyEndpoint.COLLECTION, params)

    def get_journalists(
        self,
        journalist_ids: list[int] | None = None,
        journalist_name: str | None = None,
        skip: int = 0,
        limit: int = 500,
    ) -> list[dict]:
        params = get_journalist_params(skip, limit, journalist_ids, journalist_name)
        return self._get_entities(LucyEndpoint.JOURNALIST, params)

    def get_projects(
        self,
        project_ids: list[int] | None = None,
        skip: int = 0,
        limit: int = 500,
    ) -> list[dict]:
        params = get_project_params(skip, limit, project_ids)
        return self._get_entities(LucyEndpoint.PROJECT, params)

    def get_products(
        self,
        manufacturer_id: int | None = None,
        collection_ids: list[int] | None = None,
        family_ids: list[int] | None = None,
        product_ids: list[int] | None = None,
        statuses: list[Status] | None = None,
        price_min: int | None = None,
        price_max: int | None = None,
        currency: Currency | None = None,
        skip: int = 0,
        limit: int = 500,
    ) -> list[dict]:
        params = get_product_params(
            skip,
            limit,
            manufacturer_id,
            collection_ids,
            family_ids,
            product_ids,
            statuses,
            price_min,
            price_max,
            currency,
        )
        return self._get_entities(LucyEndpoint.PRODUCT, params)

    def get_families(
        self,
        manufacturer_id: int | None = None,
        family_ids: list[int] | None = None,
        skip: int = 0,
        limit: int = 500,
    ) -> list[dict]:
        params = get_family_params(skip, limit, manufacturer_id, family_ids)
        return self._get_entities(LucyEndpoint.FAMILY, params)

    def get_creators(
        self,
        creator_ids: list[int] | None = None,
        skip: int = 0,
        limit: int = 500,
    ) -> list[dict]:
        params = get_creator_params(skip, limit, creator_ids)
        return self._get_entities(LucyEndpoint.CREATOR, params)

    def get_filters(
        self,
        filter_ids: list[int] | None = None,
        skip: int = 0,
        limit: int = 500,
    ) -> list[dict]:
        params = get_filter_params(skip, limit, filter_ids)
        return self._get_entities(LucyEndpoint.FILTER, params)

    def get_stories(
        self,
        story_ids: list[int] | None = None,
        skip: int = 0,
        limit: int = 500,
    ) -> list[dict]:
        params = get_story_params(skip, limit, story_ids)
        return self._get_entities(LucyEndpoint.STORY, params)

    def get_groups(
        self,
        group_ids: list[int] | None = None,
        skip: int = 0,
        limit: int = 500,
    ) -> list[dict]:
        params = get_group_params(skip, limit, group_ids)
        return self._get_entities(LucyEndpoint.GROUP, params)

    def get_fairs(
        self,
        fair_ids: list[int] | None = None,
        skip: int = 0,
        limit: int = 500,
    ) -> list[dict]:
        params = get_fair_params(skip, limit, fair_ids)
        return self._get_entities(LucyEndpoint.FAIR, params)
