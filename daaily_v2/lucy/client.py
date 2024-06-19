from daaily_v2.enums import Environment
from daaily_v2.http.client import Client as HttpClient
from daaily_v2.http.utility import add_authorization_header
from daaily_v2.lucy.enums import Currency, LucyEndpoint, Status, TopicEntityStage
from daaily_v2.lucy.utility import (
    extract_response_data,
    gen_collection_get_params,
    gen_creator_get_params,
    gen_distributor_get_params,
    gen_fair_get_params,
    gen_family_get_params,
    gen_filter_get_params,
    gen_group_get_params,
    gen_journalist_get_params,
    gen_manufacturer_get_params,
    gen_post_put_params,
    gen_product_get_params,
    gen_project_get_params,
    gen_request_url_with_id,
    gen_request_url_with_params,
    gen_story_get_params,
    get_lucy_v2_endpoint_url,
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

    def _create_entities(
        self, lucy_endpoint: LucyEndpoint, params: dict, data: list[dict]
    ) -> list[dict]:
        get_endpoint_url = get_lucy_v2_endpoint_url(self.environment, lucy_endpoint)
        request_url = gen_request_url_with_params(get_endpoint_url, params)
        headers = self._get_request_headers()
        response = self.http_client.post_request(request_url, data, headers)
        return extract_response_data(response)

    def _update_entities(
        self, lucy_endpoint: LucyEndpoint, params: dict, data: list[dict]
    ) -> list[dict]:
        get_endpoint_url = get_lucy_v2_endpoint_url(self.environment, lucy_endpoint)
        request_url = gen_request_url_with_params(get_endpoint_url, params)
        headers = self._get_request_headers()
        response = self.http_client.put_request(request_url, data, headers)
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
        params = gen_manufacturer_get_params(
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
        params = gen_distributor_get_params(
            skip, limit, distributor_ids, distributor_name
        )
        return self._get_entities(LucyEndpoint.DISTRIBUTOR, params)

    def get_collections(
        self,
        manufacturer_id: int | None = None,
        collection_ids: list[int] | None = None,
        skip: int = 0,
        limit: int = 500,
    ) -> list[dict]:
        params = gen_collection_get_params(skip, limit, manufacturer_id, collection_ids)
        return self._get_entities(LucyEndpoint.COLLECTION, params)

    def get_journalists(
        self,
        journalist_ids: list[int] | None = None,
        journalist_name: str | None = None,
        skip: int = 0,
        limit: int = 500,
    ) -> list[dict]:
        params = gen_journalist_get_params(skip, limit, journalist_ids, journalist_name)
        return self._get_entities(LucyEndpoint.JOURNALIST, params)

    def get_projects(
        self,
        project_ids: list[int] | None = None,
        skip: int = 0,
        limit: int = 500,
    ) -> list[dict]:
        params = gen_project_get_params(skip, limit, project_ids)
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
        params = gen_product_get_params(
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
        params = gen_family_get_params(skip, limit, manufacturer_id, family_ids)
        return self._get_entities(LucyEndpoint.FAMILY, params)

    def get_creators(
        self,
        creator_ids: list[int] | None = None,
        skip: int = 0,
        limit: int = 500,
    ) -> list[dict]:
        params = gen_creator_get_params(skip, limit, creator_ids)
        return self._get_entities(LucyEndpoint.CREATOR, params)

    def get_filters(
        self,
        filter_ids: list[int] | None = None,
        skip: int = 0,
        limit: int = 500,
    ) -> list[dict]:
        params = gen_filter_get_params(skip, limit, filter_ids)
        return self._get_entities(LucyEndpoint.FILTER, params)

    def get_stories(
        self,
        story_ids: list[int] | None = None,
        skip: int = 0,
        limit: int = 500,
    ) -> list[dict]:
        params = gen_story_get_params(skip, limit, story_ids)
        return self._get_entities(LucyEndpoint.STORY, params)

    def get_groups(
        self,
        group_ids: list[int] | None = None,
        skip: int = 0,
        limit: int = 500,
    ) -> list[dict]:
        params = gen_group_get_params(skip, limit, group_ids)
        return self._get_entities(LucyEndpoint.GROUP, params)

    def get_fairs(
        self,
        fair_ids: list[int] | None = None,
        skip: int = 0,
        limit: int = 500,
    ) -> list[dict]:
        params = gen_fair_get_params(skip, limit, fair_ids)
        return self._get_entities(LucyEndpoint.FAIR, params)

    # CREATE

    def create_manufacturers(
        self,
        new_manufacturers: list[dict],
        pubsub_stage: TopicEntityStage | None = None,
        pubsub_ordering_key: str = "",
    ):
        params = gen_post_put_params(pubsub_stage, pubsub_ordering_key)
        return self._create_entities(
            LucyEndpoint.MANUFACTURER, params, new_manufacturers
        )

    def create_distributors(
        self,
        new_distributors: list[dict],
        pubsub_stage: TopicEntityStage | None = None,
        pubsub_ordering_key: str = "",
    ):
        params = gen_post_put_params(pubsub_stage, pubsub_ordering_key)
        return self._create_entities(LucyEndpoint.DISTRIBUTOR, params, new_distributors)

    def create_collections(
        self,
        new_collections: list[dict],
        pubsub_stage: TopicEntityStage | None = None,
        pubsub_ordering_key: str | None = None,
        publish_send_status: bool | None = None,
    ):
        params = gen_post_put_params(
            pubsub_stage, pubsub_ordering_key, publish_send_status
        )
        return self._create_entities(LucyEndpoint.COLLECTION, params, new_collections)

    def create_journalists(
        self,
        new_journalists: list[dict],
        pubsub_stage: TopicEntityStage | None = None,
        pubsub_ordering_key: str | None = None,
    ):
        params = gen_post_put_params(pubsub_stage, pubsub_ordering_key)
        return self._create_entities(LucyEndpoint.JOURNALIST, params, new_journalists)

    def create_projects(self, new_projects: list[dict]):
        return self._create_entities(LucyEndpoint.PROJECT, {}, new_projects)

    def create_products(
        self,
        new_products: list[dict],
        pubsub_stage: TopicEntityStage | None = None,
        pubsub_ordering_key: str | None = None,
        publish_send_status: bool | None = None,
    ):
        params = gen_post_put_params(
            pubsub_stage, pubsub_ordering_key, publish_send_status
        )
        return self._create_entities(LucyEndpoint.PRODUCT, params, new_products)

    def create_families(
        self,
        new_families: list[dict],
        pubsub_stage: TopicEntityStage | None = None,
        pubsub_ordering_key: str | None = None,
        publish_send_status: bool | None = None,
    ):
        params = gen_post_put_params(
            pubsub_stage, pubsub_ordering_key, publish_send_status
        )
        return self._create_entities(LucyEndpoint.FAMILY, params, new_families)

    def create_creators(
        self,
        new_creators: list[dict],
        pubsub_stage: TopicEntityStage | None = None,
        pubsub_ordering_key: str | None = None,
    ):
        params = gen_post_put_params(pubsub_stage, pubsub_ordering_key)
        return self._create_entities(LucyEndpoint.CREATOR, params, new_creators)

    def create_filters(
        self,
        new_filters: list[dict],
        pubsub_stage: TopicEntityStage | None = None,
        pubsub_ordering_key: str | None = None,
    ):
        params = gen_post_put_params(pubsub_stage, pubsub_ordering_key)
        return self._create_entities(LucyEndpoint.FILTER, params, new_filters)

    def create_stories(self, new_stories: list[dict]):
        return self._create_entities(LucyEndpoint.STORY, {}, new_stories)

    def create_groups(
        self,
        new_groups: list[dict],
        pubsub_stage: TopicEntityStage | None = None,
        pubsub_ordering_key: str | None = None,
    ):
        params = gen_post_put_params(pubsub_stage, pubsub_ordering_key)
        return self._create_entities(LucyEndpoint.GROUP, params, new_groups)

    def create_fairs(self, new_fairs: list[dict]):
        return self._create_entities(LucyEndpoint.FAIR, {}, new_fairs)

    # UPDATE

    def update_manufacturers(
        self,
        existing_manufacturers: list[dict],
        pubsub_stage: TopicEntityStage | None = None,
        pubsub_ordering_key: str = "",
    ):
        params = gen_post_put_params(pubsub_stage, pubsub_ordering_key)
        return self._update_entities(
            LucyEndpoint.MANUFACTURER, params, existing_manufacturers
        )

    def update_distributors(
        self,
        existing_distributors: list[dict],
        pubsub_stage: TopicEntityStage | None = None,
        pubsub_ordering_key: str = "",
    ):
        params = gen_post_put_params(pubsub_stage, pubsub_ordering_key)
        return self._update_entities(
            LucyEndpoint.DISTRIBUTOR, params, existing_distributors
        )

    def update_collections(
        self,
        existing_collections: list[dict],
        pubsub_stage: TopicEntityStage | None = None,
        pubsub_ordering_key: str | None = None,
        publish_send_status: bool | None = None,
    ):
        params = gen_post_put_params(
            pubsub_stage, pubsub_ordering_key, publish_send_status
        )
        return self._update_entities(
            LucyEndpoint.COLLECTION, params, existing_collections
        )

    def update_journalists(
        self,
        existing_journalists: list[dict],
        pubsub_stage: TopicEntityStage | None = None,
        pubsub_ordering_key: str | None = None,
    ):
        params = gen_post_put_params(pubsub_stage, pubsub_ordering_key)
        return self._update_entities(
            LucyEndpoint.JOURNALIST, params, existing_journalists
        )

    def update_projects(self, new_projects: list[dict]):
        return self._update_entities(LucyEndpoint.PROJECT, {}, new_projects)

    def update_products(
        self,
        existing_products: list[dict],
        pubsub_stage: TopicEntityStage | None = None,
        pubsub_ordering_key: str | None = None,
        publish_send_status: bool | None = None,
        check_revision: bool | None = None,
    ):
        params = gen_post_put_params(
            pubsub_stage, pubsub_ordering_key, publish_send_status, check_revision
        )
        return self._update_entities(LucyEndpoint.PRODUCT, params, existing_products)

    def update_families(
        self,
        existing_families: list[dict],
        pubsub_stage: TopicEntityStage | None = None,
        pubsub_ordering_key: str | None = None,
        publish_send_status: bool | None = None,
        check_revision: bool | None = None,
    ):
        params = gen_post_put_params(
            pubsub_stage, pubsub_ordering_key, publish_send_status, check_revision
        )
        return self._update_entities(LucyEndpoint.FAMILY, params, existing_families)

    def update_creators(
        self,
        existing_creators: list[dict],
        pubsub_stage: TopicEntityStage | None = None,
        pubsub_ordering_key: str | None = None,
    ):
        params = gen_post_put_params(pubsub_stage, pubsub_ordering_key)
        return self._update_entities(LucyEndpoint.CREATOR, params, existing_creators)

    def update_filters(
        self,
        existing_filters: list[dict],
        pubsub_stage: TopicEntityStage | None = None,
        pubsub_ordering_key: str | None = None,
    ):
        params = gen_post_put_params(pubsub_stage, pubsub_ordering_key)
        return self._update_entities(LucyEndpoint.FILTER, params, existing_filters)

    def update_stories(self, new_stories: list[dict]):
        return self._update_entities(LucyEndpoint.STORY, {}, new_stories)

    def update_groups(
        self,
        existing_groups: list[dict],
        pubsub_stage: TopicEntityStage | None = None,
        pubsub_ordering_key: str | None = None,
    ):
        params = gen_post_put_params(pubsub_stage, pubsub_ordering_key)
        return self._update_entities(LucyEndpoint.GROUP, params, existing_groups)

    def update_fairs(self, existing_fairs: list[dict]):
        return self._update_entities(LucyEndpoint.FAIR, {}, existing_fairs)
