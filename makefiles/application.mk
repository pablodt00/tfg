tfg:
	make build-push
	make k8s-setup
	@sleep 10
	make k8s-monitoring-deploy
	@echo "✅ Monitoring deploy complete!"
	@sleep 30
	make k8s-db-deploy
	@echo "✅ Database deploy complete!"
	@sleep 30
	make k8s-migrate
	@echo "✅ Database migration complete!"
	@sleep 10
	make k8s-kafka-deploy
	@echo "✅ Kafka deploy complete!"
	@sleep 30
	make k8s-kafka-create-topic TOPIC=coingecko-prices.updates
	@echo "✅ Kafka topic creation complete!"
	make k8s-api-deploy
	@echo "✅ API Daemon deploy complete!"
	@sleep 10
	make k8s-coingecko-deploy
	@echo "✅ Coingecko API Daemon deploy complete!"
	@sleep 20
	make k8s-processor-deploy
	@echo "✅ Processor Daemon deploy complete!"
	@sleep 10
