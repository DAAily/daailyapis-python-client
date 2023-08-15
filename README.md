# Python Client For Daaily Services Apis

This package ought to include all clients of the services provided by Daaily. We will start with the `lucy` client.
This will be a rapper around the `lucy` service. Based on HTTP requests.
## Installation

```bash
pip install daaily
```

## Usage

```python
from daaily import lucy
from daaily.lucy.types import Entity

lucy_client = lucy.Client()
manufacturers = lucy_client.get_entities(Entity.MANUFACTURER, limit=50)
```

## Development

```bash
cp .env.example .env
pip install -r requirements.txt
```
