tfg:
	make build-push
	make k8s-setup
	@sleep 10
	make k8s-monitoring-deploy
	@sleep 30
	make k8s-db-deploy
	@sleep 30
	make k8s-migrate
	@sleep 10
	make k8s-kafka-deploy
	@sleep 30
	make k8s-kafka-create-topic TOPIC=coingecko-prices.updates
	make k8s-api-deploy
	@sleep 10
	make k8s-coingecko-deploy
	@sleep 10
	make k8s-processor-deploy
