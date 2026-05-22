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

k8s-kafka-ui-deploy:
	kubectl apply -f kubernetes/kafka-ui.yaml
	kubectl wait --for=condition=Available --timeout=120s deployment/kafka-ui -n kafka

k8s-kafka-ui-delete:
	kubectl delete -f kubernetes/kafka-ui.yaml

k8s-kafka-ui-open:
	kubectl port-forward --address 0.0.0.0 -n kafka svc/kafka-ui 18080:8080

k8s-kafka-broker-setup:
	kubectl apply -f https://github.com/knative-sandbox/eventing-kafka-broker/releases/download/knative-v1.12.0/eventing-kafka-controller.yaml
	kubectl apply -f https://github.com/knative-sandbox/eventing-kafka-broker/releases/download/knative-v1.12.0/eventing-kafka-broker.yaml
	kubectl wait --for=condition=Available --timeout=600s deployment/kafka-controller -n knative-eventing
	kubectl wait --for=condition=Available --timeout=600s deployment/kafka-broker-receiver -n knative-eventing
	kubectl wait --for=condition=Available --timeout=600s deployment/kafka-broker-dispatcher -n knative-eventing
