build-dev:
	docker build -f docker/common/Dockerfile -t tfg-dev .

dev-shell:
	docker run -it tfg-dev /bin/bash

test:
	docker run -it -v $$PWD:/srv -w /srv tfg-dev bash -c "PYTHONPATH=src pytest"

test-pipeline:
	docker run -i -v $$PWD:/srv -w /srv tfg-dev bash -c "PYTHONPATH=src pytest"

pylint:
	docker run --rm -i -v $$PWD:/srv -w /srv tfg-dev bash -c "PYTHONPATH=src pylint src tests"

isort-fix:
	docker run --rm -i -v $$PWD:/srv -w /srv tfg-dev bash -c "isort src tests"

black-fix:
	docker run --rm -i -v $$PWD:/srv -w /srv tfg-dev bash -c "black src tests"

precommit:
	make isort-fix
	make black-fix
	make pylint
	make test


