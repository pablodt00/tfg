k8s-setup:
	chmod +x scripts/setup_knative.sh
	./scripts/setup_knative.sh

k8s-delete:
	kind delete cluster --name tfg-knative-local

k8s-status:
	kubectl get pods -n knative-serving
	kubectl get ksvc --all-namespaces