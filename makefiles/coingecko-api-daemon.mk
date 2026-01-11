k8s-coingecko-api-daemon-deploy:
	kubectl apply -f kubernetes/configmap.yaml
	kubectl apply -f kubernetes/coingecko-api-daemon.yaml
	kubectl apply -f kubernetes/coingecko-cronjob-source.yaml

k8s-coingecko-api-daemon-delete:
	kubectl delete -f kubernetes/coingecko-cronjob-source.yaml --ignore-not-found=true
	kubectl delete -f kubernetes/coingecko-api-daemon.yaml --ignore-not-found=true

k8s-coingecko-api-daemon-logs:
	kubectl logs -l serving.knative.dev/service=coingecko-service -c coingecko-service -f

k8s-coingecko-api-daemon-status:
	kubectl get ksvc coingecko-service
	kubectl get pingsource coingecko-cronjob
	kubectl get pods -l serving.knative.dev/service=coingecko-service

k8s-coingecko-api-daemon-forward:
	kubectl port-forward service/coingecko-service 8001:8000
