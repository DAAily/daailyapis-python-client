# DAAily Lucy Client Documentation

## Classes and Methods

### Methods

The LucyClient works with resources and provides a set of exposed methods to use on each supported resource.  
The resources are as follows:
- **`get(filters: list[Filter] | None)`**
  - Get multiple resources using filters.

- **`get_by_id(resource_id: int)`**
  - Get a single resource using a resource ID.

- **`create(resources: list[dict], filters: list[Filter] | None)`**
  - Create multiple resources, also allowing the use of filters.

- **`update(resources: list[dict], filters: list[Filter] | None)`**
  - Update multiple resources, also allowing the use of filters.

---

## Usage Examples

### Get multiple resources with LucyClient

```python
from daaily.lucy import Client

# Initialize the client
client = Client(base_url="https://lucy.staging.daaily.com/api/v2")

filters = [Filter(name="limit", value="20")]
project = client.projects.get(filters)
print(f"Project: {project.json()}")
```

### Get single resource with LucyClient

```python
from daaily.lucy import Client

# Initialize the client
client = Client(base_url="https://lucy.staging.daaily.com/api/v2")

product = client.products.get_by_id(20306944)
print(f"Product: {product.json()}")
```

### Create multiple resources with LucyClient

```python
from daaily.lucy import Client

# Initialize the client
client = Client(base_url="https://lucy.staging.daaily.com/api/v2")

stories = [{"sample": "data"}]
created_stories = client.stories.create(stories)
print(f"Stories: {created_stories.json()}")
```

### Update multiple resources with LucyClient

```python
from daaily.lucy import Client

# Initialize the client
client = Client(base_url="https://lucy.staging.daaily.com/api/v2")

families = [{"sample": "data"}]
updated_families = client.families.update(20306944)
print(f"Families: {updated_families.json()}")
```