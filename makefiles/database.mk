k8s-db-deploy:
	kubectl apply -f kubernetes/database-deployment.yaml

k8s-db-shell:
	kubectl exec -it deployment/tfg-db -- psql -U tfg_user -d tfg_db

k8s-migrate:
	kubectl apply -f kubernetes/configmap.yaml
	kubectl delete job tfg-db-migration --ignore-not-found=true
	kubectl apply -f kubernetes/database-migration-job.yaml
	kubectl wait --for=condition=complete --timeout=60s job/tfg-db-migration
	kubectl logs job/tfg-db-migration