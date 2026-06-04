LOCUST_FILE  ?= tests/load/locustfile.py
API_HOST     ?= http://localhost:8080
REPORT_DIR   ?= tests/load/reports
LOCUST_LOG   ?= --loglevel INFO
LOCUST_RUN = docker run --rm -i -v $$PWD:/srv -w /srv --network host tfg bash -c

$(shell mkdir -p $(REPORT_DIR))

# ---------------------------------------------------------------------------
# Prueba 1 – Carga Sostenida
# 30 usuarios, 8 minutos, carga mixta constante.
# ---------------------------------------------------------------------------
load-test-sustained:
	@echo "==> Prueba 1: Carga Sostenida (30 users, 8 min)"
	$(LOCUST_RUN) "locust -f $(LOCUST_FILE) SustainedLoadUser \
		--host $(API_HOST) \
		--users 30 \
		--spawn-rate 5 \
		--run-time 8m \
		--headless \
		$(LOCUST_LOG) \
		--html $(REPORT_DIR)/prueba1-carga-sostenida.html \
		--csv $(REPORT_DIR)/prueba1-carga-sostenida"

# ---------------------------------------------------------------------------
# Prueba 2 – Pico de Carga
# 5 minutos: 10 → 80 → 10 usuarios (controlado por SpikeLoadShape).
# ---------------------------------------------------------------------------
load-test-spike:
	@echo "==> Prueba 2: Pico de Carga (10 → 80 → 10 users, 5 min)"
	$(LOCUST_RUN) "locust -f tests/load/shapes/spike.py \
		--host $(API_HOST) \
		--headless \
		--run-time 5m \
		$(LOCUST_LOG) \
		--html $(REPORT_DIR)/prueba2-pico-carga.html \
		--csv $(REPORT_DIR)/prueba2-pico-carga"

# ---------------------------------------------------------------------------
# Prueba 3 – Cold Start
# Espera 2 minutos (inactividad para scale-to-zero),
# luego envía 20 peticiones simultáneas durante 2 minutos.
# ---------------------------------------------------------------------------
load-test-coldstart:
	@echo "==> Prueba 3: Cold Start"
	@echo "    Esperando 2 minutos para que los pods escalen a 0..."
	@echo "    (Requiere min-scale: '0' en el Knative Service – Política B)"
	sleep 120
	@echo "    Enviando 20 peticiones simultáneas..."
	$(LOCUST_RUN) "locust -f $(LOCUST_FILE) ColdStartUser \
		--host $(API_HOST) \
		--users 20 \
		--spawn-rate 20 \
		--run-time 2m \
		--headless \
		$(LOCUST_LOG) \
		--html $(REPORT_DIR)/prueba3-cold-start.html \
		--csv $(REPORT_DIR)/prueba3-cold-start"

# ---------------------------------------------------------------------------
# Prueba 4 – Procesamiento de Eventos
# 10 minutos de tráfico ligero para observar el pipeline completo.
# ---------------------------------------------------------------------------
load-test-events:
	@echo "==> Prueba 4: Procesamiento de Eventos (10 min, tráfico ligero)"
	@echo "    Monitoriza en Grafana: http://localhost:3000"
	$(LOCUST_RUN) "locust -f $(LOCUST_FILE) EventProcessingUser \
		--host $(API_HOST) \
		--users 10 \
		--spawn-rate 2 \
		--run-time 10m \
		--headless \
		$(LOCUST_LOG) \
		--html $(REPORT_DIR)/prueba4-procesamiento-eventos.html \
		--csv $(REPORT_DIR)/prueba4-procesamiento-eventos"

# ---------------------------------------------------------------------------
# Prueba 5 – Resiliencia
# 8 minutos de carga sostenida + inyección de fallos manual al minuto 4.
# ---------------------------------------------------------------------------
load-test-resilience:
	@echo "==> Prueba 5: Resiliencia (20 users, 8 min)"
	@echo "    Inyectar fallo en otra terminal al minuto 4 con:"
	@echo "      make load-test-kill-pod"
	$(LOCUST_RUN) "locust -f $(LOCUST_FILE) ResilienceUser \
		--host $(API_HOST) \
		--users 20 \
		--spawn-rate 5 \
		--run-time 8m \
		--headless \
		$(LOCUST_LOG) \
		--html $(REPORT_DIR)/prueba5-resiliencia.html \
		--csv $(REPORT_DIR)/prueba5-resiliencia"

load-test-kill-pod:
	@echo "==> Matando pod aleatorio de api-daemon..."
	kubectl delete pod \
		$(shell kubectl get pods -l serving.knative.dev/service=api-daemon \
			--field-selector=status.phase=Running \
			-o jsonpath='{.items[0].metadata.name}')

# ---------------------------------------------------------------------------
# Prueba 6 – Escalado Horizontal
# 8 minutos: ramp lineal 10 → 100 usuarios (5 min), luego 100 → 10 (3 min).
# ---------------------------------------------------------------------------
load-test-scaling:
	@echo "==> Prueba 6: Escalado Horizontal (10 → 100 → 10 users, 8 min)"
	$(LOCUST_RUN) "locust -f tests/load/shapes/scaling.py \
		--host $(API_HOST) \
		--headless \
		--run-time 8m \
		$(LOCUST_LOG) \
		--html $(REPORT_DIR)/prueba6-escalado-horizontal.html \
		--csv $(REPORT_DIR)/prueba6-escalado-horizontal"

# ---------------------------------------------------------------------------
# Modo UI – Abre la interfaz web de Locust
# ---------------------------------------------------------------------------
load-test-ui:
	@echo "==> Locust Web UI en http://localhost:8089"
	$(LOCUST_RUN) "locust -f $(LOCUST_FILE) --host $(API_HOST) --web-port 8089"

# ---------------------------------------------------------------------------
# Suite completa (ejecuta todas las pruebas secuencialmente)
# ~47 min en total
# ---------------------------------------------------------------------------
load-test-all: load-test-sustained load-test-spike load-test-events \
               load-test-resilience load-test-scaling
	@echo "==> Todas las pruebas de carga completadas."
	@echo "    Informes disponibles en $(REPORT_DIR)/"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

load-test-status:
	@echo "==> Estado de los Knative Services:"
	kubectl get ksvc
	@echo ""
	@echo "==> Pods activos:"
	kubectl get pods -l 'serving.knative.dev/service in (api-daemon,processor-service,webapp-daemon,coingecko-service)'

load-test-clean:
	rm -rf $(REPORT_DIR)
	mkdir -p $(REPORT_DIR)

.PHONY: load-test-sustained load-test-spike load-test-coldstart load-test-events \
        load-test-resilience load-test-scaling load-test-ui load-test-all \
        load-test-status load-test-kill-pod load-test-clean
