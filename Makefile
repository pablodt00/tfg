PROJECT ?= tfg
COMPOSE_FILE=docker/docker-compose.yml
DC=docker-compose -p ${PROJECT} -f ${COMPOSE_FILE}

DOCKERFILE=docker/Dockerfile

build:
	docker build -f docker/Dockerfile -t tfg .

shell:
	${DC} run --rm shell

clean:
	${DC} down --remove-orphans

logs:
	${DC} logs -f

test:
	docker run -it -v $$PWD:/srv -w /srv tfg bash -c "PYTHONPATH=src pytest"

test-pipeline:
	docker run -i -v $$PWD:/srv -w /srv tfg bash -c "PYTHONPATH=src pytest"

pylint:
	docker run --rm -i -v $$PWD:/srv -w /srv tfg bash -c "PYTHONPATH=src pylint src tests"

isort-fix:
	docker run --rm -i -v $$PWD:/srv -w /srv tfg bash -c "isort src tests"

black-fix:
	docker run --rm -i -v $$PWD:/srv -w /srv tfg bash -c "black src tests"

precommit:
	make isort-fix
	make black-fix
	make pylint
	make test

application:
	make coingecko-api-daemon

coingecko-api-daemon:
	${DC} up -d coingecko-api-daemon
