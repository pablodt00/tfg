k8s-processor-deploy:
	kubectl apply -f kubernetes/configmap.yaml
	kubectl apply -f kubernetes/kafka.yaml
	kubectl apply -f kubernetes/kafka-broker.yaml
	kubectl apply -f kubernetes/kafka-source.yaml
	kubectl apply -f kubernetes/processor-daemon.yaml
	kubectl apply -f kubernetes/processor-trigger.yaml

k8s-processor-delete:
	kubectl delete -f kubernetes/processor-trigger.yaml --ignore-not-found=true
	kubectl delete -f kubernetes/processor-daemon.yaml --ignore-not-found=true

k8s-processor-logs:
	kubectl logs -l serving.knative.dev/service=processor-service -c processor-service -f

k8s-processor-status:
	kubectl get ksvc processor-service
	kubectl get trigger processor-trigger
	kubectl get pods -l serving.knative.dev/service=processor-service

k8s-processor-forward:
	@DEPLOYMENT=$$(kubectl get deployment -l serving.knative.dev/service=processor-service -o jsonpath='{.items[0].metadata.name}'); \
	if [ -z "$$DEPLOYMENT" ]; then \
		echo "Error: No processor-service deployment found"; \
		exit 1; \
	fi; \
	echo "Forwarding to deployment: $$DEPLOYMENT"; \
	kubectl port-forward deployment/$$DEPLOYMENT 8002:8000