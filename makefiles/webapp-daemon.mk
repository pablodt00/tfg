k8s-webapp-deploy:
	kubectl apply -f kubernetes/configmap.yaml
	kubectl apply -f kubernetes/webapp-daemon.yaml

k8s-webapp-delete:
	kubectl delete -f kubernetes/webapp-daemon.yaml

k8s-webapp-logs:
	kubectl logs -l serving.knative.dev/service=webapp-daemon -c user-container -f

k8s-webapp-status:
	kubectl get ksvc webapp-daemon
	kubectl get pods -l serving.knative.dev/service=webapp-daemon

k8s-webapp-forward:
	kubectl port-forward deployment/webapp-daemon-00001-deployment 8081:8080
