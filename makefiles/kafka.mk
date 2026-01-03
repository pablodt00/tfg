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

