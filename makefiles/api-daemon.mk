k8s-api-deploy:
	kubectl apply -f kubernetes/configmap.yaml
	kubectl apply -f kubernetes/api-daemon.yaml

k8s-api-delete:
	kubectl delete -f kubernetes/api-daemon.yaml

k8s-api-logs:
	kubectl logs -l serving.knative.dev/service=api-daemon -c user-container -f

k8s-api-status:
	kubectl get ksvc api-daemon
	kubectl get pods -l serving.knative.dev/service=api-daemon

k8s-api-forward:
	while true; do \
		POD=$$(kubectl get pod -l serving.knative.dev/service=api-daemon --field-selector=status.phase=Running -o name | head -1); \
		if [ -n "$$POD" ]; then \
			echo "Forwarding $$POD 7654->7654"; \
			kubectl port-forward --address 0.0.0.0 $$POD 7654:7654; \
		else \
			echo "No running pod found, retrying..."; \
		fi; \
		sleep 2; \
	done