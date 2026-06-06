k8s-setup:
	@command -v kind >/dev/null 2>&1 || { echo "kind not installed"; exit 1; }
	@command -v kubectl >/dev/null 2>&1 || { echo "kubectl not installed"; exit 1; }
	@if kind get clusters | grep -q "^tfg-knative-local$$"; then \
		kind delete cluster --name tfg-knative-local; \
	fi
	@echo "Creating kind cluster..."
	kind create cluster --name tfg-knative-local --config kubernetes/kind-config.yaml
	@echo "Installing Knative components..."
	kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.12.0/serving-crds.yaml
	kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.12.0/serving-core.yaml
	kubectl apply -f https://github.com/knative/net-kourier/releases/download/knative-v1.12.0/kourier.yaml
	kubectl apply -f https://github.com/knative/eventing/releases/download/knative-v1.12.0/eventing-crds.yaml
	kubectl apply -f https://github.com/knative/eventing/releases/download/knative-v1.12.0/eventing-core.yaml
	kubectl apply -f https://github.com/knative-extensions/eventing-kafka-broker/releases/download/knative-v1.12.0/eventing-kafka-controller.yaml
	kubectl apply -f https://github.com/knative-extensions/eventing-kafka-broker/releases/download/knative-v1.12.0/eventing-kafka-source.yaml
	kubectl wait --for=condition=Available deployment --all -n knative-eventing --timeout=300s
	kubectl patch configmap/config-network -n knative-serving --type merge --patch '{"data":{"ingress-class":"kourier.ingress.networking.knative.dev"}}'
	kubectl apply -f kubernetes/knative-dns.yaml
	kubectl wait --for=condition=Available deployment --all -n knative-serving --timeout=300s
	kubectl wait --for=condition=Available deployment --all -n kourier-system --timeout=300s
	@echo "Knative setup complete"

k8s-delete:
	kind delete cluster --name tfg-knative-local

k8s-status:
	kubectl get pods -n knative-serving
	kubectl get ksvc --all-namespaces