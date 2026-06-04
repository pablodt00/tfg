# Casos de Estudio: Políticas de Orquestación Knative

## Descripción del Sistema

El sistema procesa datos de criptomonedas con los siguientes componentes:
- **coingecko-service**: Obtención de datos cada 60s y publicación en Kafka. Triggereado por PingSource (1 evento/min, tráfico fijo).
- **processor-service**: Procesamiento de CloudEvents de Kafka, evaluación de alertas, envío de emails.
- **api-daemon**: API REST consumida por la webapp y los tests de carga (tráfico variable de usuarios).
- **webapp-daemon**: Interfaz Streamlit. Configuración base fija entre políticas (`min-scale: "1"`, `max-scale: "3"`).

Las políticas se aplican principalmente a **api-daemon** (tráfico de usuarios HTTP) y **processor-service** (pipeline de eventos). El coingecko-service mantiene `min-scale: "1"` en todas las políticas al tener carga fija y predecible.

El paralelismo en el pipeline de eventing se controla con el campo `consumers` en `KafkaSource` (`kafka-source.yaml`). La entrega del Trigger controla reintentos y backoff, no el paralelismo.

---

## Políticas de Orquestación

### Política A: Baja Latencia

**Objetivo**: Minimizar el tiempo de respuesta extremo a extremo del sistema.

**Configuración api-daemon** (`api-daemon.yaml`):
```yaml
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/min-scale: "3"
        autoscaling.knative.dev/max-scale: "10"
        autoscaling.knative.dev/target: "50"
        autoscaling.knative.dev/scale-down-delay: "60s"
        autoscaling.knative.dev/metric: "concurrency"
    spec:
      containerConcurrency: 50
      containers:
      - resources:
          requests:
            cpu: "300m"
            memory: "256Mi"
          limits:
            cpu: "800m"
            memory: "512Mi"
```

**Configuración processor-service** (`processor-daemon.yaml`):
```yaml
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/min-scale: "2"
        autoscaling.knative.dev/max-scale: "5"
        autoscaling.knative.dev/target: "5"
        autoscaling.knative.dev/scale-down-delay: "60s"
        autoscaling.knative.dev/metric: "concurrency"
    spec:
      containerConcurrency: 5
      containers:
      - resources:
          requests:
            cpu: "200m"
            memory: "256Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"
```

**Configuración KafkaSource** (`kafka-source.yaml`):
```yaml
spec:
  consumers: 3
```

**Configuración Trigger** (`processor-trigger.yaml`):
```yaml
spec:
  delivery:
    backoffPolicy: exponential
    backoffDelay: "PT0.5S"
    retry: 3
```

**Características**:
- Mínimo 3 réplicas de api-daemon siempre activas (sin cold starts en API)
- Mínimo 2 réplicas de processor (procesamiento inmediato de eventos)
- Target bajo (50): escala pronto antes de que cada pod se sature
- 3 consumidores Kafka en paralelo para baja latencia en el pipeline
- Recursos generosos por pod

**Métricas objetivo**:
- `request_duration_seconds` p50 < 100ms, p95 < 300ms
- `cold_start_count` = 0
- Pod count api-daemon: siempre ≥ 3
- Kafka consumer lag ≈ 0

---

### Política B: Eficiencia de Recursos

**Objetivo**: Minimizar consumo de recursos; scale-to-zero cuando no hay tráfico.

**Configuración api-daemon**:
```yaml
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/min-scale: "0"
        autoscaling.knative.dev/max-scale: "5"
        autoscaling.knative.dev/target: "150"
        autoscaling.knative.dev/scale-down-delay: "30s"
        autoscaling.knative.dev/metric: "concurrency"
        autoscaling.knative.dev/scale-to-zero-pod-retention-period: "30s"
    spec:
      containerConcurrency: 150
      containers:
      - resources:
          requests:
            cpu: "50m"
            memory: "64Mi"
          limits:
            cpu: "250m"
            memory: "256Mi"
```

**Configuración processor-service**:
```yaml
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/min-scale: "0"
        autoscaling.knative.dev/max-scale: "3"
        autoscaling.knative.dev/target: "10"
        autoscaling.knative.dev/scale-down-delay: "30s"
        autoscaling.knative.dev/metric: "concurrency"
        autoscaling.knative.dev/scale-to-zero-pod-retention-period: "30s"
    spec:
      containerConcurrency: 10
      containers:
      - resources:
          requests:
            cpu: "50m"
            memory: "64Mi"
          limits:
            cpu: "250m"
            memory: "256Mi"
```

**Configuración KafkaSource**:
```yaml
spec:
  consumers: 1
```

**Configuración Trigger**:
```yaml
spec:
  delivery:
    backoffPolicy: exponential
    backoffDelay: "PT2S"
    retry: 5
```

**Características**:
- Scale-to-zero en api-daemon y processor: 0 pods en reposo
- Recursos mínimos por pod
- Scale-down rápido (30s) para liberar recursos cuanto antes
- Un único consumidor Kafka (procesamiento secuencial)
- Más reintentos para compensar cold starts en la cadena de entrega

**Métricas objetivo**:
- Pod count: ≈ 0 en reposo, escala solo bajo demanda
- CPU/memoria totales: mínimos fuera de ráfagas
- `cold_start_duration`: latencia añadida en la primera petición tras inactividad
- `request_duration_seconds` p95 (esperable mayor que Política A)

---

### Política C: Balanceada

**Objetivo**: Compromiso equilibrado entre latencia y uso de recursos.

**Configuración api-daemon**:
```yaml
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/min-scale: "1"
        autoscaling.knative.dev/max-scale: "8"
        autoscaling.knative.dev/target: "100"
        autoscaling.knative.dev/scale-down-delay: "120s"
        autoscaling.knative.dev/metric: "concurrency"
        autoscaling.knative.dev/target-utilization-percentage: "70"
    spec:
      containerConcurrency: 100
      containers:
      - resources:
          requests:
            cpu: "150m"
            memory: "128Mi"
          limits:
            cpu: "500m"
            memory: "384Mi"
```

**Configuración processor-service**:
```yaml
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/min-scale: "1"
        autoscaling.knative.dev/max-scale: "4"
        autoscaling.knative.dev/target: "10"
        autoscaling.knative.dev/scale-down-delay: "120s"
        autoscaling.knative.dev/metric: "concurrency"
    spec:
      containerConcurrency: 10
      containers:
      - resources:
          requests:
            cpu: "100m"
            memory: "128Mi"
          limits:
            cpu: "300m"
            memory: "384Mi"
```

**Configuración KafkaSource**:
```yaml
spec:
  consumers: 2
```

**Configuración Trigger**:
```yaml
spec:
  delivery:
    backoffPolicy: exponential
    backoffDelay: "PT1S"
    retry: 4
```

**Características**:
- 1 réplica mínima (cold starts solo en réplicas adicionales al escalar)
- Target del 70% de utilización: escala antes de saturar cada pod
- 2 consumidores Kafka: paralelismo moderado
- Scale-down de 2 minutos: sin fluctuaciones bruscas

**Métricas objetivo**:
- `request_duration_seconds` p95 < 500ms
- CPU en carga sostenida: 50–70%
- Pod count api-daemon: 1–4 réplicas según carga
- Throughput RPS relativo al número de pods activos

---

### Política D: Alta Disponibilidad

**Objetivo**: Máxima resiliencia ante picos de carga y fallos de pods.

**Configuración api-daemon**:
```yaml
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/min-scale: "2"
        autoscaling.knative.dev/max-scale: "15"
        autoscaling.knative.dev/target: "80"
        autoscaling.knative.dev/scale-down-delay: "300s"
        autoscaling.knative.dev/metric: "rps"
        autoscaling.knative.dev/panic-window-percentage: "20"
        autoscaling.knative.dev/panic-threshold-percentage: "200"
    spec:
      containerConcurrency: 80
      containers:
      - resources:
          requests:
            cpu: "200m"
            memory: "256Mi"
          limits:
            cpu: "600m"
            memory: "512Mi"
```

**Configuración processor-service**:
```yaml
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/min-scale: "2"
        autoscaling.knative.dev/max-scale: "8"
        autoscaling.knative.dev/target: "5"
        autoscaling.knative.dev/scale-down-delay: "300s"
        autoscaling.knative.dev/metric: "concurrency"
    spec:
      containerConcurrency: 5
      containers:
      - resources:
          requests:
            cpu: "150m"
            memory: "256Mi"
          limits:
            cpu: "400m"
            memory: "512Mi"
```

**Configuración KafkaSource**:
```yaml
spec:
  consumers: 3
```

**Configuración Trigger**:
```yaml
spec:
  delivery:
    backoffPolicy: exponential
    backoffDelay: "PT1S"
    retry: 8
    # deadLetterSink requiere desplegar el servicio dlq-handler previamente
    # deadLetterSink:
    #   ref:
    #     apiVersion: serving.knative.dev/v1
    #     kind: Service
    #     name: dlq-handler
```

**Características**:
- Mínimo 2 réplicas en api y processor (redundancia activa)
- Métrica RPS en api-daemon: más predictivo que concurrencia ante picos súbitos
- Panic mode: si las peticiones se duplican en 20s, escala inmediatamente sin esperar la ventana estable
- 8 reintentos en Trigger para garantizar entrega ante fallos transitorios
- Scale-down lento (5 min) para absorber picos sin incurrir en cold starts

**Métricas objetivo**:
- Tasa de errores HTTP 5xx < 1% incluso durante kill de pod
- Pod count: siempre ≥ 2, escala rápido ante pico súbito
- Tiempo de recuperación observable en error rate tras `make load-test-kill-pod`
- Reintentos del Trigger (visible en logs del processor)

---

## Conjunto de Pruebas

Las pruebas se ejecutan para cada política con `make load-test-*`. Cada prueba genera un informe HTML en `tests/load/reports/`.

### 1. Carga Sostenida (8 min)
- **Descripción**: Carga constante para verificar comportamiento en estado estable y capacidad de escalado sostenido
- **Configuración**: 30 usuarios concurrentes, mix de GET /coins y POST /alerts
- **Comando**: `make load-test-sustained`

### 2. Pico de Carga (5 min)
- **Descripción**: Ráfaga súbita para medir velocidad de escalado y recuperación
- **Configuración**: 10 → 80 → 10 usuarios (1 min baseline, 2 min pico, 2 min recuperación)
- **Comando**: `make load-test-spike`

### 3. Cold Start (≈4 min)
- **Descripción**: Medir latencia de primera petición tras inactividad
- **Configuración**: 2 min de espera para permitir scale-to-zero, luego 20 peticiones simultáneas durante 2 min
- **Nota**: Principalmente diferenciadora en Política B (min-scale=0). En otras políticas mide la latencia de arranque de réplicas adicionales.
- **Comando**: `make load-test-coldstart`

### 4. Procesamiento de Eventos (10 min)
- **Descripción**: Observar el pipeline completo a frecuencia normal del CronJob (1 evento/min)
- **Configuración**: 10 usuarios en AlertHeavyBehavior para poblar alertas en BD mientras el pipeline procesa
- **Comando**: `make load-test-events`

### 5. Resiliencia (8 min)
- **Descripción**: Carga sostenida con kill de pod a mitad de prueba para medir recuperación
- **Configuración**: 20 usuarios; ejecutar `make load-test-kill-pod` en el minuto 4
- **Comando**: `make load-test-resilience`

### 6. Escalado Horizontal (8 min)
- **Descripción**: Rampa lineal para observar el comportamiento del autoescalado
- **Configuración**: 10 → 100 usuarios en 5 min, luego 100 → 10 en 3 min
- **Comando**: `make load-test-scaling`
