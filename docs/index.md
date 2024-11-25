# DAAily Python Client Documentation

Welcome to the official documentation for the `daailyapis-python-client`. This documentation provides a comprehensive reference for developers using the client to interact with DAAily APIs.

---

## Table of Contents

- [Getting Started](#getting-started)
- [Installation](#installation)
- [Client Libraries](#client-libraries)
- [Classes and Methods](#classes-and-methods)
- [Usage Examples](#usage-examples)
- [Support and Contribution](#support-and-contribution)

---

## Getting Started

The `daailyapis-python-client` is designed for seamless integration with DAAily Services. Follow the instructions below to get started with installation and configuration.

---

## Installation

To install the latest version:

```bash
pip install git+ssh://git@github.com/DAAily/daailyapis-python-client.git
```

---

## Client Libraries

### Lucy Client

The `LucyClient` is the primary interface for interacting with the `lucy` service.

---

## Classes and Methods

### LucyClient

#### Methods

- **`__init__(api_key: str)`**
  - Initializes the client with your API key.

- **`search(query: str) -> dict`**
  - Executes a search request.

- **`get_resource(resource_id: str) -> dict`**
  - Fetches a resource by ID.

- **`create_resource(data: dict) -> dict`**
  - Creates a new resource.

#### Example Usage

```python
from daailyapis import LucyClient

client = LucyClient(api_key="your_api_key")
results = client.search(query="example")
print(results)
```

---

## Usage Examples

### Searching with LucyClient

```python
client = LucyClient(api_key="your_api_key")
response = client.search(query="data science")
print(response)
```

---

## Support and Contribution

Have questions or want to contribute? Open an issue or create a pull request on our [GitHub repository](https://github.com/DAAily/daailyapis-python-client).

---

Generated with ❤️ using Sphinx and maintained by the DAAily Team.

