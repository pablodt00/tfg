# Proyecto TFG - Crypto Alerts Dashboard

## Descripción

Este proyecto es un sistema distribuido para el monitoreo y análisis de criptomonedas, desarrollado como Trabajo de Fin de Grado. La arquitectura está basada en microservicios que se comunican a través de Kafka y Knative Eventing, y se despliegan en Kubernetes utilizando Knative Serving para la gestión de servicios serverless.

## Estructura del Proyecto

### 📁 `src/`
Contiene el código fuente de la aplicación, organizado en módulos:

- **`api/`**: Daemon y servicio REST API para exponer endpoints HTTP
  - `api_daemon.py`: Proceso principal del servicio API
  - `api_service.py`: Lógica del servicio
  - `endpoints/`: Endpoints REST (alertas, monedas, health checks)

- **`app/`**: Aplicación web frontend
  - `webapp_daemon.py`: Daemon de la aplicación web desarrollado con `streamlit`

- **`gateway/`**: Gateway para la integración con la API externa de CoinGecko
  - `coingecko_api_daemon.py`: Daemon para consumir datos de CoinGecko
  - `coingecko_service.py`: Lógica del servicio que publica a Kafka
  - `endpoints/`: Endpoints de salud y gestión del servicio

- **`processor/`**: Procesador de eventos de criptomonedas y notificaciones
  - `processor_daemon.py`: Daemon de procesamiento que recibe CloudEvents
  - `processor_service.py`: Lógica de procesamiento y gestión de alertas
  - `email_service.py`: Servicio de envío de emails con Resend
  - `endpoints/`: Endpoints para recibir eventos y health checks

- **`common/`**: Módulos compartidos
  - `client/`: Clientes para la API externa de CoinGecko
  - `config/`: Configuración de la aplicación
  - `consumers/`: Consumidores de Kafka
  - `producers/`: Productores de Kafka para publicar eventos
  - `database/`: Acceso a base de datos con repositorios
  - `observability/`: Métricas de Prometheus y logging estructurado
  - `schemas/`: Esquemas de datos de base de datos

### 📁 `kubernetes/`
Manifiestos de Kubernetes para el despliegue:
- **Knative Services** (`*-daemon.yaml`): Servicios serverless con autoescalado
  - `api-daemon.yaml`: Servicio API REST
  - `coingecko-api-daemon.yaml`: Gateway de CoinGecko
  - `processor-daemon.yaml`: Procesador de eventos
  - `webapp-daemon.yaml`: Aplicación web
- **Kafka y Eventing**:
  - `kafka.yaml`: Despliegue de RedPanda (broker de Kafka)
  - `kafka-broker.yaml`: Broker de Knative Eventing
  - `kafka-source.yaml`: Fuente de eventos desde Kafka
  - `processor-trigger.yaml`: Trigger que conecta eventos al processor
  - `coingecko-cronjob-source.yaml`: Fuente de eventos programados (CronJob)
- **Base de datos**:
  - `database-deployment.yaml`: PostgreSQL
  - `database-migration-job.yaml`: Jobs de migración
- **Monitoreo**:
  - `prometheus.yaml`: Servidor de métricas
  - `prometheus-rbac.yaml`: Permisos para Prometheus
  - `grafana.yaml`: Plataforma de visualización
- **Configuración**:
  - `configmap.yaml`: Variables de entorno compartidas
  - `knative-dns.yaml`: Configuración DNS para Knative
  - `kind-config.yaml`: Configuración del cluster local

### 📁 `tests/`
Suite de tests unitarios organizados por módulo

### 📁 `docker/`
Configuración de Docker para desarrollo local:
- `Dockerfile`: Imagen Docker de la aplicación
- `docker-compose.yml`: Orquestación de servicios
- `local.env`: Variables de entorno locales

### 📁 `kubernetes/grafana-dashboards/`
Dashboards de Grafana en formato JSON para monitorización:
- `infrastructure.json`: Dashboard de infraestructura general
- `api-daemon.json`: Métricas del servicio API
- `coingecko-api-daemon.json`: Métricas del gateway de CoinGecko
- `processor-daemon.json`: Métricas del procesador
- `webapp-daemon.json`: Métricas de la aplicación web

### 📁 `makefiles/`
Makefiles modulares para diferentes componentes:
- Gestión de daemons individuales (deploy, delete, logs, forward, status)
- Configuración de Kafka y Knative Eventing
- Gestión de base de datos y migraciones
- Configuración de monitoreo (Prometheus y Grafana)
- Tareas de desarrollo y testing

### 📁 `scripts/`
Scripts bash para ejecutar los diferentes daemons con `uvicorn`

### 📁 `docs/`
Documentación del proyecto:
- Diagramas de arquitectura
- Guías de configuración (ej: entorno Kubernetes con Kind)

## Inicio Rápido

### Requisitos Previos
- Python 3.10+
- Docker y Docker Compose
- Kubernetes (kind)
- Make
- Cuenta de Docker Hub
- Cuenta de Resend (para envío de emails)
- Modificación de `DOCKER_USER` por nombre de usuario de Docker Hub en todo el proyecto
- Modificación de `RESEND_API_KEY` en `kubernetes/configmap.yaml`
- Modificación de `COINGECKO_API_KEY` en `kubernetes/configmap.yaml`

### Ejecución

Para arrancar todo el sistema completo una vez cumplidos los requisitos previos:

```bash
make tfg
```

Este comando iniciará todos los componentes necesarios:
- Cluster de Kubernetes con Kind
- Knative Serving y Knative Eventing
- Kafka (RedPanda) como broker de mensajes
- Base de datos PostgreSQL
- Todos los servicios Knative:
  - API REST
  - Gateway de CoinGecko
  - Procesador de eventos
  - Aplicación web
- Sistema de monitoreo (Prometheus y Grafana)
- Fuentes de eventos y triggers

### Comandos Útiles

```bash
# Ejecutar checkeos antes de hacer commit (pylint, tests, ...)
make precommit

# Ver logs de servicios específicos:
make k8s-api-logs
make k8s-coingecko-api-daemon-logs
make k8s-processor-logs
make k8s-webapp-logs

# Port-forwarding para acceder a servicios:
make k8s-grafana-forward         # Grafana UI en http://localhost:3000
make k8s-prometheus-forward      # Prometheus UI en http://localhost:9090
make k8s-webapp-forward          # WebApp en http://localhost:8501
make k8s-api-forward             # API REST en http://localhost:8080
make k8s-coingecko-api-daemon-forward  # Gateway CoinGecko en http://localhost:8001
make k8s-processor-forward       # Processor en http://localhost:8002

# Verificar estado de servicios:
make k8s-api-status
make k8s-coingecko-api-daemon-status
make k8s-processor-status
make k8s-webapp-status

# Gestión de Kafka:
make k8s-kafka-topics            # Listar topics
make k8s-kafka-consume TOPIC=<topic>  # Consumir mensajes de un topic
make k8s-kafka-logs              # Ver logs de RedPanda

# Acceder a la shell de la base de datos:
make k8s-db-shell

# Parar y eliminar el sistema desplegado:
make k8s-delete
```

## Monitoreo

Una vez desplegado el sistema, puedes acceder a:
- **Grafana**: `http://localhost:3000` (admin/admin)
  - Dashboards preconfigurados para cada servicio
  - Métricas de infraestructura
- **Prometheus**: `http://localhost:9090`
  - Métricas raw de todos los servicios
- **Webapp**: `http://localhost:8501`
  - Interfaz de usuario para gestión de alertas

## Arquitectura

El sistema sigue una arquitectura basada en eventos con Knative y los siguientes componentes:

1. **CoinGecko API Daemon** (Knative Service):
   - Obtiene datos de criptomonedas de la API pública de CoinGecko
   - Publica eventos a Kafka topic `coingecko-prices.updates`
   - Triggered por CronJobSource cada minuto

2. **Kafka \+ Knative Eventing**:
   - **RedPanda**: Broker de Kafka ligero
   - **KafkaSource**: Consume mensajes de Kafka y los convierte a CloudEvents
   - **Kafka Broker**: Broker de Knative que recibe CloudEvents
   - **Trigger**: Enruta eventos del broker al processor

3. **Processor Daemon** (Knative Service):
   - Recibe CloudEvents vía HTTP desde el trigger
   - Procesa datos de criptomonedas
   - Actualiza base de datos con precios y cambios porcentuales
   - Evalúa alertas configuradas
   - Envía emails cuando se disparan alertas

4. **API Daemon** (Knative Service):
   - Expone endpoints REST para gestión de alertas y consulta de monedas
   - CRUD de alertas de usuario
   - Consulta de precios actuales

5. **WebApp Daemon** (Knative Service):
   - Interfaz de usuario con Streamlit
   - Gestión visual de alertas
   - Dashboard de monitoreo de criptomonedas

6. **PostgreSQL**:
   - Almacenamiento persistente de:
     - Precios históricos de monedas
     - Alertas de usuarios
     - Configuración de usuarios

7. **Prometheus \+ Grafana**:
   - Observabilidad y monitoreo
   - Métricas custom de cada servicio
   - Dashboards preconfigrados

### Flujo de Datos

1. **CronJobSource** dispara evento cada minuto → **CoinGecko Service**
2. **CoinGecko Service** llama a API → Publica a **Kafka topic**
3. **KafkaSource** consume de Kafka → Envía CloudEvent a **Kafka Broker**
4. **Trigger** filtra eventos → Enruta a **Processor Service**
5. **Processor Service** recibe CloudEvent → Procesa datos:
   - Actualiza **PostgreSQL** con nuevos precios
   - Evalúa alertas configuradas
   - Envía **emails** si se disparan alertas

### Ventajas de la Arquitectura

- **Serverless**: Knative Serving escala automáticamente (incluso a 0)
- **Desacoplamiento**: Servicios se comunican vía eventos
- **Resilencia**: Kafka garantiza entrega de mensajes
- **Escalabilidad**: Cada servicio escala independientemente
- **Observabilidad**: Métricas y logs centralizados

## Desarrollo

### Variables de Entorno

Las principales variables se configuran en `kubernetes/configmap.yaml`:

```yaml
KAFKA_BOOTSTRAP_SERVERS: "redpanda.kafka.svc.cluster.local:9092"
COINGECKO_KAFKA_TOPIC: "coingecko-prices.updates"
RESEND_API_KEY: "api-key"
FROM_EMAIL: "email@ejemplo.com"
DB_HOST: "postgresql-service.default.svc.cluster.local"
# ... más variables
```

### Testing Local

```bash
# Ejecutar formatters, linters y tests antes de commit
make precommit
```

## Pruebas de Carga (Load Testing)

Las pruebas de carga se realizan con [Locust](https://locust.io/) y están diseñadas para ejecutarse contra el sistema desplegado en Kubernetes.

### Requisitos

Locust está incluido en la imagen Docker del proyecto (`requirements/requirements.txt`).
No es necesario instalarlo en el host. Los comandos `make load-test-*` ejecutan locust
dentro del contenedor Docker con `--network host` para poder alcanzar el port-forward.

### Acceso desde fuera del cluster

Locust se ejecuta **fuera del cluster Kubernetes** y accede a la API mediante `kubectl port-forward`. Esto es perfectamente válido para pruebas de carga: el tráfico entra al cluster a través del pod de destino, Knative detecta la carga y escala los servicios igual que en producción.

```bash
# Terminal 1 – mantener el port-forward activo
make k8s-api-forward   # API en http://localhost:8080
```

### Comandos disponibles

| Comando | Descripción | Duración |
|---|---|---|
| `make load-test-sustained` | Prueba 1 – Carga sostenida (30 users) | 8 min |
| `make load-test-spike` | Prueba 2 – Pico de carga (10→80→10 users) | 5 min |
| `make load-test-coldstart` | Prueba 3 – Cold start (idle 2 min + burst de 20) | ~4 min |
| `make load-test-events` | Prueba 4 – Procesamiento de eventos (pipeline) | 10 min |
| `make load-test-resilience` | Prueba 5 – Resiliencia (20 users + kill pod) | 8 min |
| `make load-test-scaling` | Prueba 6 – Escalado horizontal (10→100→10 users) | 8 min |
| `make load-test-ui` | Modo UI interactivo en http://localhost:8089 | manual |
| `make load-test-all` | Suite completa secuencial | ~47 min |
| `make load-test-status` | Estado de Knative Services y pods activos | — |

```bash
# Ejemplo: ejecutar la prueba de carga sostenida
make load-test-sustained

# Personalizar host (por defecto http://localhost:8080)
make load-test-sustained API_HOST=http://mi-host:8080
```

Los informes HTML y CSV se generan automáticamente en `tests/load/reports/`.

### Estructura de archivos de prueba

```
tests/load/
  locustfile.py          # Clases de usuario (SustainedLoadUser, ColdStartUser, etc.)
  shapes/
    spike.py             # LoadTestShape para Prueba 2 (pico de carga)
    scaling.py           # LoadTestShape para Prueba 6 (escalado horizontal)
```

> **Nota sobre `LoadTestShape`**: Locust sólo permite una shape activa por invocación.
> Por eso las pruebas con rampas de carga (Pruebas 2 y 6) viven en ficheros separados.

### Políticas de Orquestación (casos de estudio)

Las pruebas deben ejecutarse para cada política definida en `docs/casos_estudio.md`.
Para cambiar de política, editar las anotaciones del Knative Service correspondiente y re-desplegar:

```bash
# Editar kubernetes/api-daemon.yaml con los valores de la política deseada
kubectl apply -f kubernetes/api-daemon.yaml
kubectl apply -f kubernetes/processor-daemon.yaml
# ... etc.
```

#### Notas de implementación Knative

| Campo en casos_estudio.md | Campo real en Kubernetes | Recurso |
|---|---|---|
| `parallelism` (eventing delivery) | `consumers` | `kafka-source.yaml` |
| `deadLetterSink.ref.name: dlq-handler` | Requiere desplegar un servicio `dlq-handler` | `processor-trigger.yaml` |
| `autoscaling.knative.dev/minScale` | `autoscaling.knative.dev/min-scale` | Anotaciones del Knative Service |

- **`parallelism`** en la spec de `delivery` de un `Trigger`/`Broker` **no es un campo válido** en la API de Knative Eventing. El paralelismo de consumidores se controla en `KafkaSource` mediante el campo `consumers` (ver `kubernetes/kafka-source.yaml`).
- **`deadLetterSink`** para la Política D requiere que exista un servicio `dlq-handler` desplegado. Está comentado en `kubernetes/processor-trigger.yaml` hasta que se cree dicho servicio.
- La anotación correcta es `min-scale` (con guión), no `minScale` — ambas son aceptadas por Knative pero `min-scale` es el estándar oficial.

## Autor
Pablo Durán