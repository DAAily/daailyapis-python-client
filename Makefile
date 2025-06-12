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
	venv/bin/python -m samples.lucy.add_about_to_manufacturer

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
	venv/bin/python -m samples.lucy.add_or_update_manufacturer_image

sample-lucy-11:
	venv/bin/python -m samples.lucy.determine_field_owner_on_product

sample-lucy-12:
	venv/bin/python -m samples.lucy.upload_product_image_to_gcs

sample-lucy-13:
	venv/bin/python -m samples.lucy.upload_product_pdf_to_gcs

sample-lucy-14:
	venv/bin/python -m samples.lucy.upload_product_cad_to_gcs
	
sample-lucy-15:
	venv/bin/python -m samples.lucy.add_address_to_manufacturer

sample-lucy-16:
	venv/bin/python -m samples.lucy.add_or_update_product_image

sample-lucy-17:
	venv/bin/python -m samples.lucy.add_or_update_family_image

sample-lucy-18:
	venv/bin/python -m samples.lucy.get_filtered_families

sample-lucy-19:
	venv/bin/python -m samples.lucy.change_status_manufacturer_image

sample-lucy-20:
	venv/bin/python -m samples.lucy.create_attribute

sample-lucy-21:
	venv/bin/python -m samples.lucy.update_attributes

sample-lucy-22:
	venv/bin/python -m samples.lucy.add_or_update_product_attributes

sample-lucy-23:
	venv/bin/python -m samples.lucy.determine_product_score_up_to_date

sample-lucy-24:
	venv/bin/python -m samples.lucy.search_attributes

sample-lucy-25:
	venv/bin/python -m samples.lucy.get_filtered_products

sample-franklin-1:
	venv/bin/python -m samples.franklin.predict_group

sample-score-1:
	venv/bin/python -m samples.score.get_product_scores

build:
	$(info NOTE: Keep in mind to increment the version when doing a new build)
	python3 -m build

publish:
	python3 -m twine upload --repository-url https://europe-west3-python.pkg.dev/one-data-project/daailyapis-python-client/ dist/* --skip-existing

