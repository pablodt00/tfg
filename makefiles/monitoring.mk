k8s-monitoring-deploy:
	kubectl apply -f kubernetes/monitoring/prometheus-rbac.yaml
	kubectl apply -f kubernetes/monitoring/prometheus.yaml
	kubectl apply -f kubernetes/monitoring/grafana.yaml

k8s-monitoring-delete:
	kubectl delete -f kubernetes/monitoring/grafana.yaml --ignore-not-found=true
	kubectl delete -f kubernetes/monitoring/prometheus.yaml --ignore-not-found=true
	kubectl delete -f kubernetes/monitoring/prometheus-rbac.yaml --ignore-not-found=true

k8s-monitoring-status:
	kubectl get pods -n monitoring
	kubectl get svc -n monitoring

k8s-grafana-forward:
	kubectl port-forward -n monitoring svc/grafana 3000:3000

k8s-prometheus-forward:
	kubectl port-forward -n monitoring svc/prometheus 9090:9090

k8s-monitoring-logs-prometheus:
	kubectl logs -n monitoring -l app=prometheus -f

k8s-monitoring-logs-grafana:
	kubectl logs -n monitoring -l app=grafana -f