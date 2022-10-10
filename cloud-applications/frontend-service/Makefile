init:
	npm init .

install:
	npm install

css:
	npm run build:css

docker-build:
	# rm -rf node_modules || true
	# rm -rf dist/* || true
	docker run --volume `pwd`:/opt/project --user `id -u`:`id -g` --workdir /opt/project --rm -it node:16-buster bash -c "npm install && npm run build-clean"
