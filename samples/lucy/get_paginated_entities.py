import json
import time

from daaily.lucy.client import Client
from daaily.lucy.constants import LUCY_V2_BASE_URL_STAGING
from daaily.lucy.models import Filter
from daaily.transport import Response


def get_skip_query(skip: int) -> tuple[int, int]:
    limit = 500
    lskip = limit * skip
    return lskip, limit


def handle_entity_response_data(
    response: Response, entities: list[dict]
) -> tuple[list[dict], bool]:
    if response.status == 200:
        data = json.loads(response.data.decode("utf-8"))
        entities.extend(data)
        more_data = True
    else:
        more_data = False
    return entities, more_data


def main():
    lucy_client = Client(base_url=LUCY_V2_BASE_URL_STAGING)
    """Get entity data from Lucy while using pagination for mass retrieval"""
    skip = 0
    more_data = True
    entities = []

    total_start_time = time.perf_counter()

    while more_data:
        lskip, limit = get_skip_query(skip)
        skip_filter = Filter(name="skip", value=str(lskip))
        limit_filter = Filter(name="limit", value=str(limit))

        start_time = time.perf_counter()
        response = lucy_client.materials.get(
            filters=[skip_filter, limit_filter],
        )

        end_time = time.perf_counter()
        elapsed_time_ms = (end_time - start_time) * 1000
        print(f"API call {skip + 1} took {elapsed_time_ms:.2f} ms")

        entities, more_data = handle_entity_response_data(response, entities)
        if not more_data:
            break
        skip += 1

    total_end_time = time.perf_counter()
    total_elapsed_time_ms = (total_end_time - total_start_time) * 1000
    print(f"Total time: {total_elapsed_time_ms:.2f} ms")
    print(len(entities))


if __name__ == "__main__":
    main()
