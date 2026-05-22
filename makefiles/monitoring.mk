k8s-monitoring-deploy:
	kubectl apply -f kubernetes/prometheus-rbac.yaml
	kubectl apply -f kubernetes/prometheus.yaml
	kubectl delete configmap grafana-dashboards -n monitoring --ignore-not-found=true
	kubectl create configmap grafana-dashboards \
	  --from-file=kubernetes/grafana-dashboards/ \
	  --namespace=monitoring
	kubectl apply -f kubernetes/grafana.yaml

k8s-monitoring-delete:
	kubectl delete -f kubernetes/grafana.yaml --ignore-not-found=true
	kubectl delete configmap grafana-dashboards -n monitoring --ignore-not-found=true
	kubectl delete -f kubernetes/prometheus.yaml --ignore-not-found=true
	kubectl delete -f kubernetes/prometheus-rbac.yaml --ignore-not-found=true

k8s-monitoring-status:
	kubectl get pods -n monitoring
	kubectl get svc -n monitoring

k8s-grafana-forward:
	kubectl port-forward --address 0.0.0.0 -n monitoring svc/grafana 3000:3000

k8s-prometheus-forward:
	kubectl port-forward --address 0.0.0.0 -n monitoring svc/prometheus 9091:9090

k8s-monitoring-logs-prometheus:
	kubectl logs -n monitoring -l app=prometheus -f

k8s-monitoring-logs-grafana:
	kubectl logs -n monitoring -l app=grafana -f