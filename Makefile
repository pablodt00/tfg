build-dev:
	docker build -f docker/common/Dockerfile -t tfg-dev .

dev-shell:
	docker run -it tfg-dev /bin/bash

test:
	docker run -i -v $$PWD:/srv -w /srv tfg-dev bash -c "PYTHONPATH=src pytest"

pylint:
	docker run --rm -it -v $$PWD:/srv -w /srv tfg-dev bash -c "PYTHONPATH=src pylint src tests"
