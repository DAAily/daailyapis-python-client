# Python Client For Daaily Services Apis

This package ought to include all clients of the services provided by Daaily. We will start with the `lucy` client.
This will be a rapper around the `lucy` service. Based on HTTP requests.
## Installation


## Installation
Latest unstable release
```bash
pip install git+ssh://git@github.com/DAAily/daailyapis-python-client.git
```

Latest stable release
```bash
pip install git+ssh://git@github.com/DAAily/daailyapis-python-client.git@v1.3.0
```

## Usage
For usage please have a look at the samples part of the samples folder.

## Development

```bash
cp .env.example .env
pip install -r tests/requirements.txt
```

NOTE: Before publishing an new version, make sure that the development changes are merged into the main (production) branch.

## Push New Version

Increment version by doing the following steps (ensure you have gcloud installed and authenticated):
```bash
source venv/bin/activate
pip install keyrings.google-artifactregistry-auth
pip install build
pip install twine
python -m build
python -m twine upload --repository-url https://europe-west3-python.pkg.dev/one-data-project/daailyapis-python-client/ dist/* --skip-existing
```
