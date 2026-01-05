PROJECT ?= tfg
COMPOSE_FILE=docker/docker-compose.yml
DC=docker-compose -p ${PROJECT} -f ${COMPOSE_FILE}
DOCKERFILE=docker/Dockerfile
DOCKER_USER=DOCKER_USER

include makefiles/api-daemon.mk
include makefiles/application.mk
include makefiles/coingecko-api-daemon.mk
include makefiles/database.mk
include makefiles/development.mk
include makefiles/kafka.mk
include makefiles/knative.mk
include makefiles/monitoring.mk
include makefiles/processor-daemon.mk
include makefiles/webapp-daemon.mk
