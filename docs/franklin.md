# DAAily Franklin Client Documentation

## Classes and Methods

### Methods

The FranklinClient works with utility functions.  
The utility functions are as follows:
- **`predict_product_group(image_path: str, product_name: str, product_text: str, model_type: str)`**
  - Predict product groups using various parameters.

---

## Usage Examples

### Predict product groups with FranklinClient

```python
from daaily.franklin import Client

# Initialize the client
client = Client(base_url="https://franklin.staging.daaily.com/api/v1")

image_path = "https://storage.googleapis.com/m-on-staging/3100089/product/1006023/minotti_held-armchair-i-pouf-_d0057ae6.jpeg"
product_name = "held-armchair-i-pouf"
product_text = "Product text of held"
model_type = "furniture"
product_groups = client.predict_product_group(image_path, product_name, product_text, model_type)
print(f"Product groups: {product_groups.json()}")
```