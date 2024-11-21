# Python Client For Daaily Services Apis

This package ought to include all clients of the services provided by Daaily. We will start with the `lucy` client.
This will be a rapper around the `lucy` service. Based on HTTP requests.


## Installation

<b>Requires local pytho version: ">=3.10"</b>

Initialize & activate virtual environment:
```bash
python -m venv venv
venv/bin/activate
```

Latest unstable release
```bash
pip install git+ssh://git@github.com/DAAily/daailyapis-python-client.git
```

Latest stable release
```bash
pip install git+ssh://git@github.com/DAAily/daailyapis-python-client.git@v1.3.0
```

Install required python packages:
```bash
cp .env.example .env
pip install -r tests/requirements.txt
```

## Usage
For usage please have a look at the samples part of the samples readme file: [SAMPLES.md](./SAMPLES.md)

## Push New Version

Increment version by doing the following steps (ensure you have gcloud installed and authenticated):

- Manually increment the version in `daaily/version.py`. Check the naming convension at https://github.com/DAAily/daailyapis-python-client/releases
- Merge the new changes (including the version increment) into the main branch (production).
- Run the following:

```bash
source venv/bin/activate
pip install keyrings.google-artifactregistry-auth
pip install build
pip install twine
python -m build
python -m twine upload --repository-url https://europe-west3-python.pkg.dev/one-data-project/daailyapis-python-client/ dist/* --skip-existing
```
