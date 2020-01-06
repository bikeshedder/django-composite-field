default: dist

clean:
	rm -rf build django_composite_field.egg-info dist .tox

sdist:
	python setup.py sdist
	
bdist_wheel:
	python setup.py bdist_wheel

dist: clean sdist bdist_wheel

upload: dist
	python setup.py sdist bdist_wheel upload
