upload:
	python setup.py sdist upload

all:
	python setup.py sdist upload
	python setup.py egg_info bdist_egg upload
	rm -rf dist/ build/

clean:
	rm -rf dist/ build/
