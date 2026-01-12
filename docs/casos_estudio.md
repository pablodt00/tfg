# Casos de Estudio: Políticas de Orquestación Knative

## Descripción del Sistema

El sistema procesa datos de criptomonedas con los siguientes componentes:
- **coingecko-api-daemon**: Obtención de datos cada 60s y publicación en Kafka
- **processor-daemon**: Procesamiento de eventos, cálculo de cambios temporales y envío de alertas
- **api-daemon**: API backend para el frontend
- **webapp-daemon**: Interfaz de usuario

## Políticas de Orquestación

### Política A: Baja Latencia

**Objetivo**: Minimizar el tiempo de respuesta extremo a extremo del sistema.

**Configuración Knative Serving**:
```yaml
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/min-scale: "3"
        autoscaling.knative.dev/max-scale: "10"
        autoscaling.knative.dev/target: "50"
        autoscaling.knative.dev/scale-down-delay: "30s"
        autoscaling.knative.dev/metric: "concurrency"
    spec:
      containers:
      - resources:
          requests:
            cpu: "500m"
            memory: "512Mi"
          limits:
            cpu: "1000m"
            memory: "1Gi"
      containerConcurrency: 50
```

**Configuración Knative Eventing**:
```yaml
spec:
  delivery:
    backoffPolicy: exponential
    backoffDelay: "PT0.5S"
    retry: 3
  parallelism: 5
```

**Características**:
- Mínimo 3 réplicas siempre activas (sin cold starts)
- Escalado agresivo con target bajo (50 peticiones concurrentes)
- Delay de scale-down de 30s para evitar fluctuaciones
- Recursos generosos por pod
- Paralelismo alto en procesamiento de eventos

**Métricas Relevantes**:
- `latency_p50`, `latency_p95`, `latency_p99` (percentiles de latencia)
- `cold_start_count` (debe ser 0)
- `request_duration_seconds`
- `event_processing_duration_seconds`
- `queue_depth` (profundidad de cola Kafka)
- `alert_delivery_time` (tiempo desde detección hasta envío)

---

### Política B: Eficiencia de Recursos

**Objetivo**: Maximizar la utilización de recursos y minimizar costes.

**Configuración Knative Serving**:
```yaml
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/min-scale: "0"
        autoscaling.knative.dev/max-scale: "5"
        autoscaling.knative.dev/target: "200"
        autoscaling.knative.dev/scale-down-delay: "10m"
        autoscaling.knative.dev/metric: "concurrency"
        autoscaling.knative.dev/scale-to-zero-pod-retention-period: "5m"
    spec:
      containers:
      - resources:
          requests:
            cpu: "100m"
            memory: "128Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"
      containerConcurrency: 200
```

**Configuración Knative Eventing**:
```yaml
spec:
  delivery:
    backoffPolicy: exponential
    backoffDelay: "PT2S"
    retry: 5
  parallelism: 1
```

**Características**:
- Scale-to-zero habilitado
- Target alto de concurrencia (200)
- Recursos mínimos por pod
- Scale-down lento (10 minutos)
- Procesamiento secuencial de eventos

**Métricas Relevantes**:
- `cpu_utilization_percent` (debe estar >70%)
- `memory_utilization_percent` (debe estar >70%)
- `pod_count` (número de réplicas activas)
- `cost_per_transaction` (recursos consumidos / peticiones)
- `cold_start_count` y `cold_start_duration`
- `resource_waste_ratio` (capacidad no utilizada)

---

### Política C: Balanceada

**Objetivo**: Compromiso entre latencia y eficiencia de recursos.

**Configuración Knative Serving**:
```yaml
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/min-scale: "1"
        autoscaling.knative.dev/max-scale: "8"
        autoscaling.knative.dev/target: "100"
        autoscaling.knative.dev/scale-down-delay: "2m"
        autoscaling.knative.dev/metric: "concurrency"
        autoscaling.knative.dev/target-utilization-percentage: "70"
    spec:
      containers:
      - resources:
          requests:
            cpu: "250m"
            memory: "256Mi"
          limits:
            cpu: "750m"
            memory: "768Mi"
      containerConcurrency: 100
```

**Configuración Knative Eventing**:
```yaml
spec:
  delivery:
    backoffPolicy: exponential
    backoffDelay: "PT1S"
    retry: 4
  parallelism: 3
```

**Características**:
- Mínimo 1 réplica (cold starts ocasionales)
- Target moderado (100)
- Recursos equilibrados
- Scale-down moderado (2 minutos)
- Paralelismo medio

**Métricas Relevantes**:
- `latency_p95` (objetivo: <500ms)
- `cpu_utilization_percent` (objetivo: 50-70%)
- `memory_utilization_percent` (objetivo: 50-70%)
- `throughput_requests_per_second`
- `pod_count` y `scaling_events_count`
- `cost_efficiency_score` (throughput / recursos)

---

### Política D: Alta Disponibilidad y Resiliencia

**Objetivo**: Garantizar disponibilidad del sistema ante picos de carga y fallos.

**Configuración Knative Serving**:
```yaml
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/min-scale: "2"
        autoscaling.knative.dev/max-scale: "15"
        autoscaling.knative.dev/target: "80"
        autoscaling.knative.dev/scale-down-delay: "5m"
        autoscaling.knative.dev/metric: "rps"
        autoscaling.knative.dev/panic-window-percentage: "20"
        autoscaling.knative.dev/panic-threshold-percentage: "200"
    spec:
      containers:
      - resources:
          requests:
            cpu: "300m"
            memory: "384Mi"
          limits:
            cpu: "800m"
            memory: "896Mi"
      containerConcurrency: 80
```

**Configuración Knative Eventing**:
```yaml
spec:
  delivery:
    backoffPolicy: exponential
    backoffDelay: "PT1S"
    retry: 8
    deadLetterSink:
      ref:
        kind: Service
        name: dlq-handler
  parallelism: 4
```

**Características**:
- Mínimo 2 réplicas para redundancia
- Métrica basada en RPS (requests per second)
- Panic mode configurado para escalado rápido ante picos
- Máximo alto de réplicas (15)
- Reintentos abundantes y Dead Letter Queue
- Paralelismo alto

**Métricas Relevantes**:
- `availability_percent` (objetivo: >99.5%)
- `error_rate` (debe ser <0.5%)
- `retry_count` y `dlq_messages_count`
- `scaling_velocity` (rapidez de escalado)
- `recovery_time_seconds` (tras fallos)
- `concurrent_requests_peak`
- `queue_latency` (tiempo en cola Kafka)

---

## Conjunto de Pruebas Estándar

Las siguientes pruebas deben ejecutarse para **todas las políticas**:

### 1. Prueba de Carga Sostenida
- **Duración**: 30 minutos
- **Descripción**: Carga constante de consultas al API y creación de alertas
- **Configuración**:
  - 50 usuarios concurrentes
  - Creación de 10 alertas/minuto
  - Consultas a diferentes endpoints del API
  
### 2. Prueba de Pico de Carga
- **Duración**: 15 minutos
- **Descripción**: Incremento súbito de carga
- **Configuración**:
  - Inicio: 10 usuarios
  - Pico (min 5-10): 200 usuarios
  - Descenso: vuelta a 10 usuarios

### 3. Prueba de Cold Start
- **Duración**: 20 minutos
- **Descripción**: Medir comportamiento tras inactividad
- **Configuración**:
  - 10 minutos sin tráfico
  - Envío de 50 peticiones simultáneas
  - Medir primera respuesta

### 4. Prueba de Procesamiento de Eventos
- **Duración**: 1 hora
- **Descripción**: Verificar procesamiento completo del pipeline
- **Configuración**:
  - Frecuencia normal del cronjob (60s)
  - 100 alertas configuradas en BD
  - Monitorizar cola Kafka y envío de emails

### 5. Prueba de Resiliencia
- **Duración**: 30 minutos
- **Descripción**: Inyección de fallos
- **Configuración**:
  - Simular caída de pods (kill aleatorio)
  - Latencia artificial en API externa (500ms-2s)
  - Errores HTTP 5xx en 5% de peticiones

### 6. Prueba de Escalado Horizontal
- **Duración**: 45 minutos
- **Descripción**: Carga incremental para forzar escalado
- **Configuración**:
  - Incremento lineal: 10 → 300 usuarios en 30 min
  - Descenso: 300 → 10 usuarios en 15 min

