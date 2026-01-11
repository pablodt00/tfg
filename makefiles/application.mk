tfg:
	make build-push
	make k8s-setup
	@sleep 5
	make k8s-monitoring-deploy k8s-db-deploy k8s-kafka-deploy
	@sleep 60
	@echo "✅ Prometheus & Grafana deployed"
	make k8s-kafka-create-topic TOPIC=coingecko-prices.updates
	make k8s-kafka-broker-setup
	@echo "✅ Kafka deployed"
	make k8s-migrate
	@echo "✅ Database deployed"
	@sleep 10
	make k8s-api-deploy k8s-webapp-deploy
	@echo "✅ API Daemon deployed"
	@echo "✅ Webapp Daemon deployed"
	make k8s-coingecko-api-daemon-deploy k8s-processor-deploy
	@echo "✅ Coingecko API Daemon deployed"
	@echo "✅ Processor Daemon deployed"
	@sleep 20
	@echo "🎉 All services deployed successfully"
