 



all:
	python run_all.py

coverage:
	rm -rf .coverage htmlcov/
	python-coverage run --source "neurounits" run_all.py
	python-coverage html
