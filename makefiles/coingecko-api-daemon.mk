k8s-coingecko-deploy:
	kubectl apply -f kubernetes/coingecko-daemon/configmap.yaml
	kubectl apply -f kubernetes/coingecko-daemon/deployment.yaml
	kubectl apply -f kubernetes/kafka-broker.yaml
	kubectl apply -f kubernetes/kafka-source.yaml

k8s-coingecko-delete:
	kubectl delete -f kubernetes/kafka-source.yaml --ignore-not-found=true
	kubectl delete -f kubernetes/kafka-broker.yaml --ignore-not-found=true
	kubectl delete -f kubernetes/coingecko-daemon/deployment.yaml --ignore-not-found=true
	kubectl delete -f kubernetes/coingecko-daemon/configmap.yaml --ignore-not-found=true

k8s-coingecko-logs:
	kubectl logs -l app=coingecko-daemon -f

k8s-coingecko-status:
	kubectl get deployment coingecko-daemon
	kubectl get pods -l app=coingecko-daemon
	kubectl get kafkasource coingecko-kafka-source
	kubectl get broker kafka-broker