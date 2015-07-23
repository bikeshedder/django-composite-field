default: dist

clean:
	rm -rf build dinbrief.egg-info dist

sdist:
	python setup.py sdist
	
bdist_wheel:
	python setup.py bdist_wheel

dist: clean sdist bdist_wheel

upload:
	twine upload dist/*

release: dist upload
