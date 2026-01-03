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