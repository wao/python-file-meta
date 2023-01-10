default: install

install : build-gem

build-gem:
	poetry build

