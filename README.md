# Proyecto TFG - Crypto Alerts Dashboard

## Descripción

Este proyecto es un sistema distribuido para el monitoreo y análisis de criptomonedas, desarrollado como Trabajo de Fin de Grado. La arquitectura está basada en microservicios que se comunican a través de Kafka y HTTP, y se despliegan en Kubernetes.

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
  - `coingecko_service.py`: Lógica del servicio
  - `coingecko_controller.py`: Controlador del demonio

- **`processor/`**: Procesador de eventos de criptomonedas y notificaciones
  - `processor_daemon.py`: Daemon de procesamiento
  - `processor_service.py`: Lógica de procesamiento
  - `email_service.py`: Servicio de envío de emails

- **`common/`**: Módulos compartidos
  - `client/`: Clientes para la API externa de CoinGecko
  - `config/`: Configuración de la aplicación
  - `consumers/`: Consumidores de Kafka
  - `producers/`: Productores de Kafka
  - `database/`: Acceso a base de datos
  - `observability/`: Métricas y logging
  - `schemas/`: Esquemas de datos de base de datos

### 📁 `kubernetes/`
Manifiestos de Kubernetes para el despliegue:
- Deployments de los daemons (API, processor, webapp, CoinGecko)
- Configuración de Kafka y Knative
- Deployment de base de datos y migraciones
- Configuración de Prometheus y Grafana para monitoreo
- ConfigMaps y servicios

### 📁 `tests/`
Suite de tests unitarios organizados por módulo

### 📁 `docker/`
Configuración de Docker para desarrollo local:
- `Dockerfile`: Imagen Docker de la aplicación
- `docker-compose.yml`: Orquestación de servicios
- `local.env`: Variables de entorno locales

### 📁 `kubernetes/grafana-dashboards/`
Dashboards de Grafana en formato JSON para monitorización:
- Dashboard de infraestructura
- Dashboards específicos por daemon

### 📁 `makefiles/`
Makefiles modulares para diferentes componentes:
- Gestión de daemons individuales
- Configuración de Kafka y Knative
- Gestión de base de datos
- Configuración de monitoreo
- Tareas de desarrollo

### 📁 `scripts/`
Scripts auxiliares para ejecutar los diferentes daemons

### 📁 `docs/`
Documentación del proyecto:
- Diagramas de arquitectura
- Guías de configuración (ej: entorno Kubernetes)

## Inicio Rápido

### Requisitos Previos
- Python 3.10+
- Docker y Docker Compose
- Kubernetes (kind)
- Make
- Cuenta de Docker Hub
- Modificación de 'DOCKER_USER' por nombre de usuario de Docker Hub en todo el proyecto

### Ejecución

Para arrancar todo el sistema completo una vez cumplidos los requisitos previos:

```bash
make tfg
```

Este comando iniciará todos los componentes necesarios:
- Cluster de Kubernetes
- Kafka y Knative
- Base de datos PostgreSQL
- Todos los daemons (API, Gateway, Processor, WebApp)
- Sistema de monitoreo (Prometheus y Grafana)

### Comandos Útiles

```bash
# Ejecutar checkeos antes de hacer commit (pylint, tests, ...)
make precommit

# Ver en local Grafana UI desplegada:
make k8s-grafana-forward

# Ver en local Prometheus UI desplegada:
make k8s-prometheus-forward

# Ver en local Webapp UI desplegada:
make k8s-webapp-forward

# Ver en local API desplegada:
make k8s-api-forward

# Acceder a la shell de la base de datos:
make k8s-db-shell

# Parar y eliminar el sistema desplegado
make k8s-delete
```

## Monitoreo

Una vez desplegado el sistema (principales elementos):
- **Grafana**: `http://localhost:3000`
- **Prometheus**: `http://localhost:9090`
- **Webapp**: `http://localhost:8501`

## Arquitectura

El sistema sigue una arquitectura basada en eventos con los siguientes componentes:

1. **CoinGecko API Daemon**: Obtiene datos de criptomonedas de la API pública de CoinGecko
2. **Processor Daemon**: Procesa eventos, trabaja con la base de datos y gestiona alertas
3. **API Daemon**: Expone endpoints REST
4. **WebApp Daemon**: Interfaz de usuario
5. **Kafka**: Bus de eventos
6. **PostgreSQL**: Almacenamiento persistente
7. **Prometheus + Grafana**: Observabilidad

## Autor
Pablo Durán