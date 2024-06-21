make:
	python setup.py bdist_wheel --universal
	python setup.py sdist
	python setup.py bdist

upload:
	twine upload dist/*