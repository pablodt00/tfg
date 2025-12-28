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
	@if [ -z "${SERVICE}" ]; then \
		echo "Tailing logs for all services. Usage: make logs SERVICE=<service-name>"; \
		${DC} logs -f; \
	else \
		echo "Tailing logs for service: ${SERVICE}"; \
		${DC} logs -f ${SERVICE}; \
	fi


test:
	${DC} run --rm test

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
	make processor-daemon

coingecko-api-daemon:
	${DC} up -d coingecko-api-daemon

api-daemon:
	${DC} up -d api-daemon

kafka:
	${DC} up -d kafka
	make kafka-create-topic TOPIC=coingecko-prices.updates
	make kafka-topics

kafka-topics:
	${DC} exec kafka kafka-topics --list --bootstrap-server kafka:9092

kafka-create-topic:
	@if [ -z "${TOPIC}" ]; then \
		echo "Please provide a topic name. Usage: make kafka-create-topic TOPIC=<topic-name>"; \
		exit 1; \
	fi
	${DC} exec kafka kafka-topics --create --topic ${TOPIC} --partitions 1 --replication-factor 1 --bootstrap-server kafka:9092

kafka-inspect-topic:
	@if [ -z "${TOPIC}" ]; then \
		echo "Please provide a topic name. Usage: make kafka-inspect-topic TOPIC=<topic-name>"; \
		exit 1; \
	fi
	${DC} exec kafka kafka-console-consumer --bootstrap-server kafka:9092 --topic ${TOPIC} --from-beginning

clean-pycache:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete

processor-daemon:
	${DC} up -d processor-daemon

run-db:
	${DC} up -d tfg-db

db-shell:
	${DC} run --rm tfg-db-shell

clear-db:
	${DC} run --rm clear-tfg-db

	${DC} run --rm alembic -c src/common/database/alembic/alembic.ini upgrade head

create-migration:
	@if [ -z "${MSG}" ]; then \
		echo "Please provide a migration message. Usage: make create-migration MSG=\"your message\""; \
		exit 1; \
	fi
	${DC} run --rm alembic -c src/common/database/alembic/alembic.ini revision --autogenerate -m "${MSG}"

migrate:
	${DC} run --rm alembic -c src/common/database/alembic/alembic.ini upgrade head


# Kubernetes / Knative targets

k8s-setup:
	chmod +x scripts/setup_knative.sh
	./scripts/setup_knative.sh

k8s-delete:
	kind delete cluster --name tfg-knative-local

k8s-status:
	kubectl get pods -n knative-serving
	kubectl get ksvc --all-namespaces

k8s-db-deploy:
	kubectl apply -f kubernetes/database-deployment.yaml

k8s-db-shell:
	kubectl exec -it deployment/tfg-db -- psql -U tfg_user -d tfg_db
