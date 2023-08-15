# Python Client For Daaily Services Apis

## Installation

```bash
pip install daaily
```

## Usage

```python
from daaily.lucy import Lucy
from daaily.lucy.types import Entity

lucy = Lucy()
manufacturers = lucy.get_entities(Entity.MANUFACTURER, limit=50)
```

## Development

```bash
cp .env.example .env
pip install -r requirements.txt
```
