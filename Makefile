include .env

install: 
	python3 -m venv venv
	venv/bin/pip install -r tests/requirements.txt

test:
	venv/bin/python -m pytest

sample-lucy-1:
	venv/bin/python -m samples.lucy.get_entities_from_lucy

sample-lucy-2:
	venv/bin/python -m samples.lucy.get_filtered_manufacturers

sample-lucy-3:
	venv/bin/python -m samples.lucy.add_image_to_product

sample-lucy-4:
	venv/bin/python -m samples.lucy.get_product_by_id

sample-lucy-5:
	venv/bin/python -m samples.lucy.add_file_to_temp_bucket

sample-lucy-6:
	venv/bin/python -m samples.lucy.get_products_async

sample-lucy-7:
	venv/bin/python -m samples.lucy.get_filtered_materials

sample-lucy-8:
	venv/bin/python -m samples.lucy.create_manufacturer

sample-lucy-9:
	venv/bin/python -m samples.lucy.get_manufacturer_by_domain

sample-lucy-10:
	venv/bin/python -m samples.lucy.add_image_to_manufacturer

sample-franklin-1:
	venv/bin/python -m samples.franklin.predict_group

sample-score-1:
	venv/bin/python -m samples.score.get_product_scores

build:
	$(info NOTE: Keep in mind to increment the version when doing a new build)
	python3 -m build

publish:
	python3 -m twine upload --repository-url https://europe-west3-python.pkg.dev/one-data-project/daailyapis-python-client/ dist/* --skip-existing

