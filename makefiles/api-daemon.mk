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
	kubectl port-forward --address 0.0.0.0 deployment/api-daemon-00001-deployment 7654:7654