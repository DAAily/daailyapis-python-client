# Python Client For Daaily Services Apis

This package ought to include all clients of the services provided by Daaily. We will start with the `lucy` client.
This will be a rapper around the `lucy` service. Based on HTTP requests.

Official Documentation: [DaailyAPIs Python Client Documentation](https://docs.google.com/document/d/1fHtorz-6bWObdFUTnX11r9TcU_Nq0AxWujec6NxcZkw/edit?tab=t.0)


## Installation

<b>Requires local python version: ">=3.10"</b>

Latest unstable release:
```bash
pip install git+ssh://git@github.com/DAAily/daailyapis-python-client.git
```

Latest stable release:
```bash
pip install git+ssh://github.com/DAAily/daailyapis-python-client.git@v1.12.0#egg=daaily
```
  
In case you want to work with the score client you need to install additional dependencies:
```bash
pip install git+ssh://github.com/DAAily/daailyapis-python-client.git@v1.12.0#egg=daaily[score]
```


## Usage
For usage please have a look at the samples part of the samples readme file: [SAMPLES.md](./SAMPLES.md)

## Development
### Install Extra Dependencies
```bash
python -m venv venv
venv/bin/activate
pip install -e ".[score]"
```

### Run Tests
```bash
python -m venv venv
venv/bin/activate
cp .env.example .env
pip install -r tests/requirements.txt
```

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
