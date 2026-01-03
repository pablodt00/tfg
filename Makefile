PROJECT ?= tfg
COMPOSE_FILE=docker/docker-compose.yml
DC=docker-compose -p ${PROJECT} -f ${COMPOSE_FILE}

DOCKERFILE=docker/Dockerfile

DOCKER_USER=DOCKER_USER

build:
	docker build -f docker/Dockerfile -t tfg .

build-push:
	docker login
	make build
	docker tag tfg:latest ${DOCKER_USER}/tfg:latest
	docker push ${DOCKER_USER}/tfg:latest

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


# Kubernetes / Knative commands

k8s-setup:
	chmod +x scripts/setup_knative.sh
	./scripts/setup_knative.sh

k8s-delete:
	kind delete cluster --name tfg-knative-local

k8s-status:
	kubectl get pods -n knative-serving
	kubectl get ksvc --all-namespaces


# Database in kubernetes

k8s-db-deploy:
	kubectl apply -f kubernetes/database-deployment.yaml

k8s-db-shell:
	kubectl exec -it deployment/tfg-db -- psql -U tfg_user -d tfg_db

k8s-migrate:
	kubectl delete job tfg-db-migration --ignore-not-found=true
	kubectl apply -f kubernetes/database-migration-job.yaml
	kubectl wait --for=condition=complete --timeout=60s job/tfg-db-migration
	kubectl logs job/tfg-db-migration


# API Daemon in Knative

k8s-api-deploy:
	kubectl apply -f kubernetes/api-daemon/configmap.yaml
	kubectl apply -f kubernetes/api-daemon/service.yaml

k8s-api-delete:
	kubectl delete -f kubernetes/api-daemon/service.yaml
	kubectl delete -f kubernetes/api-daemon/configmap.yaml

k8s-api-logs:
	kubectl logs -l serving.knative.dev/service=api-daemon -c user-container -f

k8s-api-status:
	kubectl get ksvc api-daemon
	kubectl get pods -l serving.knative.dev/service=api-daemon

k8s-api-forward:
	kubectl port-forward deployment/api-daemon-00001-deployment 8080:8000


# =========================
# Kafka on Kubernetes
# =========================

k8s-kafka-deploy:
	kubectl apply -f kubernetes/kafka.yaml

k8s-kafka-delete:
	kubectl delete -f kubernetes/kafka.yaml

k8s-kafka-status:
	kubectl get pods -n kafka
	kubectl get svc -n kafka

k8s-kafka-logs:
	kubectl logs -n kafka deployment/redpanda -f

k8s-kafka-shell:
	kubectl exec -it -n kafka deployment/redpanda -- bash

k8s-kafka-topics:
	kubectl exec -it -n kafka deployment/redpanda -- \
	rpk topic list

k8s-kafka-create-topic:
	@if [ -z "${TOPIC}" ]; then \
		echo "Usage: make k8s-kafka-create-topic TOPIC=<topic>"; \
		exit 1; \
	fi
	kubectl exec -it -n kafka deployment/redpanda -- \
	rpk topic create ${TOPIC}

k8s-kafka-consume:
	@if [ -z "${TOPIC}" ]; then \
		echo "Usage: make k8s-kafka-consume TOPIC=<topic>"; \
		exit 1; \
	fi
	kubectl exec -it -n kafka deployment/redpanda -- \
		rpk topic consume ${TOPIC} --offset start



# =========================
# Coingecko API Daemon in Knative
# =========================

k8s-coingecko-deploy:
	kubectl apply -f kubernetes/coingecko-daemon/configmap.yaml
	kubectl apply -f kubernetes/coingecko-daemon/deployment.yaml
	kubectl apply -f kubernetes/kafka-broker.yaml
	kubectl apply -f kubernetes/kafka-source.yaml

k8s-coingecko-delete:
	kubectl delete -f kubernetes/kafka-source.yaml --ignore-not-found=true
	kubectl delete -f kubernetes/kafka-broker.yaml --ignore-not-found=true
	kubectl delete -f kubernetes/coingecko-daemon/deployment.yaml --ignore-not-found=true
	kubectl delete -f kubernetes/coingecko-daemon/configmap.yaml --ignore-not-found=true

k8s-coingecko-logs:
	kubectl logs -l app=coingecko-daemon -f

k8s-coingecko-status:
	kubectl get deployment coingecko-daemon
	kubectl get pods -l app=coingecko-daemon
	kubectl get kafkasource coingecko-kafka-source
	kubectl get broker kafka-broker

# ========================
# Processor Daemon in Knative
# ========================

k8s-processor-deploy:
	kubectl apply -f kubernetes/processor-daemon/configmap.yaml
	kubectl apply -f kubernetes/processor-daemon/deployment.yaml

k8s-processor-delete:
	kubectl delete -f kubernetes/processor-daemon/deployment.yaml --ignore-not-found=true
	kubectl delete -f kubernetes/processor-daemon/configmap.yaml --ignore-not-found=true

k8s-processor-logs:
	kubectl logs -l app=processor-daemon -f

k8s-processor-status:
	kubectl get deployment processor-daemon
	kubectl get pods -l app=processor-daemon


