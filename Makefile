make:
	python setup.py bdist_wheel --universal
	python setup.py sdist

upload:
	twine upload dist/*