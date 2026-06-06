# Casos de Estudio: Políticas de Orquestación Knative

## Descripción del Sistema

- **coingecko-service**: Fetch de precios cada 60s (PingSource). Tráfico fijo y predecible.
- **processor-service**: Consume CloudEvents de Kafka; evalúa alertas, escribe en BD, envía emails.
- **api-daemon**: API REST para el frontend. Tráfico variable de usuarios.
- **webapp-daemon**: Interfaz Streamlit. Conexiones largas (una por sesión de usuario).

Cada política define la configuración de los cuatro servicios de forma coherente con su objetivo.

**Cómo aplicar**: editar las anotaciones y recursos en los `.yaml` de `kubernetes/` y ejecutar `kubectl apply -f kubernetes/<servicio>.yaml`. Para `kafka-source.yaml` y `processor-trigger.yaml` aplicar también sus cambios.

**Métricas**: Locust genera la carga HTTP. Las métricas de rendimiento se recogen de **Prometheus/Grafana**: latencias de Knative Serving (`revision_request_latencies`), pod counts (`autoscaler_actual_pods`), CPU/memoria (`container_cpu_usage_seconds_total`, `container_memory_usage_bytes`), consumer lag de Kafka y `autoscaler_panic_mode` (Política D).

---

## Políticas

Las anotaciones van en `spec.template.metadata.annotations`. `containerConcurrency` y `resources` van en `spec.template.spec` (el primero a nivel de `spec`, los segundos dentro de `containers`).

---

### Política A: Baja Latencia

**Objetivo**: El sistema siempre listo para responder. Sin cold starts, escalado agresivo ante picos.

| Parámetro | api-daemon | processor-service | coingecko-service | webapp-daemon |
|---|---|---|---|---|
| `min-scale` | `"3"` | `"2"` | `"1"` | `"2"` |
| `max-scale` | `"10"` | `"5"` | `"2"` | `"5"` |
| `target` | `"50"` | `"5"` | `"5"` | `"20"` |
| `metric` | `concurrency` | `concurrency` | `concurrency` | `concurrency` |
| `scale-down-delay` | `"60s"` | `"60s"` | — | `"60s"` |
| `containerConcurrency` | `50` | `5` | `5` | `20` |
| CPU request/limit | 300m / 800m | 200m / 500m | 200m / 500m | 200m / 500m |
| Memoria request/limit | 256Mi / 512Mi | 256Mi / 512Mi | 256Mi / 512Mi | 256Mi / 512Mi |

**KafkaSource** — `consumers: 3`

**Trigger delivery**:
```yaml
backoffPolicy: exponential
backoffDelay: "PT0.5S"
retry: 3
```

**Características**:
- 3 réplicas de api-daemon y 2 de processor y webapp siempre activas → ninguna petición espera a un cold start.
- Target bajo (50 para api, 5 para processor): Knative escala antes de saturar cada pod.
- 3 consumers Kafka: eventos procesados en paralelo → menor consumer lag.
- Recursos generosos por pod: menor riesgo de CPU throttling.

**Qué observar**:
- p50/p95/p99 de `revision_request_latencies` → deben ser los más bajos de todas las políticas.
- `autoscaler_actual_pods` ≥ min-scale en todo momento.
- Kafka consumer lag ≈ 0.

---

### Política B: Eficiencia de Recursos

**Objetivo**: Consumir el mínimo de recursos. Scale-to-zero cuando no hay tráfico.

| Parámetro | api-daemon | processor-service | coingecko-service | webapp-daemon |
|---|---|---|---|---|
| `min-scale` | `"0"` | `"0"` | `"0"` | `"0"` |
| `max-scale` | `"5"` | `"3"` | `"1"` | `"3"` |
| `target` | `"150"` | `"20"` | `"5"` | `"30"` |
| `metric` | `concurrency` | `concurrency` | `concurrency` | `concurrency` |
| `scale-down-delay` | `"30s"` | `"30s"` | `"30s"` | `"30s"` |
| `scale-to-zero-pod-retention-period` | `"30s"` | `"30s"` | `"30s"` | `"30s"` |
| `containerConcurrency` | `150` | `20` | `5` | `30` |
| CPU request/limit | 50m / 250m | 50m / 250m | 50m / 200m | 50m / 200m |
| Memoria request/limit | 64Mi / 256Mi | 64Mi / 256Mi | 64Mi / 256Mi | 64Mi / 256Mi |

> **Nota sobre coingecko-service**: con un evento por minuto y scale-down-delay de 30s, en la práctica es probable que no llegue a escalar a 0 (la ventana de inactividad apenas da tiempo). El min-scale=0 se configura igualmente por coherencia con la política.

**KafkaSource** — `consumers: 1`

**Trigger delivery**:
```yaml
backoffPolicy: exponential
backoffDelay: "PT2S"
retry: 5
```

**Características**:
- Todo puede llegar a 0 pods en reposo → recursos de clúster mínimos cuando el sistema está inactivo.
- Target alto (150 para api, 20 para processor): cada pod absorbe mucha más carga antes de escalar.
- Recursos mínimos por pod: requests muy bajos → pods caben en nodos pequeños.
- 1 solo consumer Kafka: procesamiento secuencial de eventos.
- Más reintentos en el Trigger para tolerar cold starts en la cadena de entrega (el processor puede estar arrancando cuando llega un evento).

**Qué observar**:
- `autoscaler_actual_pods` = 0 durante inactividad → confirma scale-to-zero.
- Pico de latencia p99 en la prueba de cold start → coste de arrancar desde cero.
- CPU y memoria totales del clúster: mínimas fuera de ráfagas.
- Kafka consumer lag bajo picos (1 consumer puede acumularlo).

---

### Política C: Balanceada

**Objetivo**: Un pod siempre disponible en cada servicio. Escalado moderado y predecible.

| Parámetro | api-daemon | processor-service | coingecko-service | webapp-daemon |
|---|---|---|---|---|
| `min-scale` | `"1"` | `"1"` | `"1"` | `"1"` |
| `max-scale` | `"8"` | `"4"` | `"2"` | `"3"` |
| `target` | `"100"` | `"10"` | `"5"` | `"20"` |
| `target-utilization-percentage` | `"70"` | `"70"` | — | `"70"` |
| `metric` | `concurrency` | `concurrency` | `concurrency` | `concurrency` |
| `scale-down-delay` | `"120s"` | `"120s"` | — | `"120s"` |
| `containerConcurrency` | `100` | `10` | `5` | `20` |
| CPU request/limit | 150m / 500m | 100m / 300m | 100m / 300m | 100m / 300m |
| Memoria request/limit | 128Mi / 384Mi | 128Mi / 384Mi | 128Mi / 384Mi | 128Mi / 384Mi |

**KafkaSource** — `consumers: 2`

**Trigger delivery**:
```yaml
backoffPolicy: exponential
backoffDelay: "PT1S"
retry: 4
```

**Características**:
- 1 réplica mínima en todos los servicios: sin cold start en el pod de guardia, pero réplicas adicionales sí arrancan en frío.
- `target-utilization-percentage: 70` → Knative escala cuando un pod alcanza el 70% de su target, dejando margen de seguridad.
- Scale-down moderado (2 min): evita fluctuaciones sin retener pods innecesariamente.
- 2 consumers Kafka: paralelismo moderado en el pipeline.

**Qué observar**:
- Latencia p95 (objetivo: <500ms en carga sostenida).
- CPU utilization en pods activos: 50–70% en estado estable.
- `autoscaler_desired_pods` vs `autoscaler_actual_pods`: cuánto tarda en converger.
- Pod count total en el clúster (equilibrio respecto a Políticas A y B).

---

### Política D: Alta Disponibilidad

**Objetivo**: Resiliencia ante picos súbitos y fallos de pods. El sistema se recupera rápido.

| Parámetro | api-daemon | processor-service | coingecko-service | webapp-daemon |
|---|---|---|---|---|
| `min-scale` | `"2"` | `"2"` | `"1"` | `"2"` |
| `max-scale` | `"15"` | `"8"` | `"2"` | `"5"` |
| `target` | `"80"` | `"5"` | `"5"` | `"20"` |
| `metric` | `rps` | `concurrency` | `concurrency` | `concurrency` |
| `scale-down-delay` | `"300s"` | `"300s"` | `"60s"` | `"300s"` |
| `panic-window-percentage` | `"20"` | — | — | — |
| `panic-threshold-percentage` | `"200"` | — | — | — |
| `containerConcurrency` | `80` | `5` | `5` | `20` |
| CPU request/limit | 200m / 600m | 150m / 400m | 150m / 400m | 150m / 400m |
| Memoria request/limit | 256Mi / 512Mi | 256Mi / 512Mi | 256Mi / 512Mi | 256Mi / 512Mi |

**KafkaSource** — `consumers: 3`

**Trigger delivery**:
```yaml
backoffPolicy: exponential
backoffDelay: "PT1S"
retry: 8
# deadLetterSink:
#   ref:
#     apiVersion: serving.knative.dev/v1
#     kind: Service
#     name: dlq-handler
```

**Características**:
- Mínimo 2 réplicas en api, processor y webapp: un pod puede caer sin downtime.
- Métrica `rps` en api-daemon: más reactiva ante picos que la concurrencia (detecta el aumento antes de que los pods se saturen).
- Panic mode en api-daemon: si el tráfico se duplica en una ventana de 20s, el autoscaler escala inmediatamente sin esperar la ventana estable de 60s.
- Scale-down lento (5 min): no se pierde capacidad al bajar el tráfico, el sistema absorbe el siguiente pico sin escalar desde cero.
- 8 reintentos en el Trigger: el processor puede estar reiniciando y los eventos se reintentarán hasta entregarse.

**Qué observar**:
- Tasa de errores HTTP 5xx antes, durante y después de `make load-test-kill-pod` → objetivo: <1%.
- `autoscaler_panic_mode` = 1 durante la prueba de pico → confirma que el panic mode se activa.
- `autoscaler_actual_pods` siempre ≥ 2.
- Tiempo hasta que error_rate vuelve a 0 tras kill de pod (recuperación).

---

## Conjunto de Pruebas

Las mismas 6 pruebas se ejecutan para cada política. Esto permite comparar el comportamiento del sistema bajo condiciones idénticas de carga.

### 1. Carga Sostenida — `make load-test-sustained` (8 min)
30 usuarios concurrentes, mix de GET /coins y POST /alerts. Mide el comportamiento en estado estable: latencia, throughput y pod count una vez el autoscaler ha convergido.

### 2. Pico de Carga — `make load-test-spike` (5 min)
10 → 80 → 10 usuarios (1 min baseline, 2 min pico, 2 min recuperación). Mide la velocidad de escalado ante una ráfaga y la velocidad de scale-down posterior.

### 3. Cold Start — `make load-test-coldstart` (~4 min)
2 min de inactividad + burst de 20 usuarios simultáneos durante 2 min. En Política B (min-scale=0) mide el cold start real desde cero. En las demás mide el arranque de réplicas adicionales.

### 4. Pipeline de Eventos — `make load-test-events` (10 min)
10 usuarios en AlertHeavyBehavior para mantener alertas activas en BD. El CronJob dispara el pipeline cada 60s (~10 ciclos). Observar en Grafana: consumer lag de Kafka, pod count del processor, tiempo de procesamiento por evento.

### 5. Resiliencia — `make load-test-resilience` (8 min)
20 usuarios sostenidos. Ejecutar `make load-test-kill-pod` en otra terminal al minuto 4. Mide la recuperación ante fallo: cuánto tarda en volver a 0 errores y si Knative levanta un pod de reemplazo.

### 6. Escalado Horizontal — `make load-test-scaling` (8 min)
Rampa lineal 10 → 100 usuarios en 5 min, luego 100 → 10 en 3 min. Mide la suavidad y velocidad del escalado automático en ambas direcciones.
