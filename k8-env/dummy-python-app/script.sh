#!/usr/bin/env bash
set -e

# ==============================
# CONFIGURACIÓN
# ==============================
DOCKER_USER="<tu_usuario>"
APP_NAME="dummy-python-app"
APP_IMAGE="docker.io/${DOCKER_USER}/${APP_NAME}:latest"
NAMESPACE="default"
KOURIER_NS="kourier-system"
KNATIVE_NS="knative-serving"

echo "🚀 Desplegando ${APP_NAME} en Knative (Minikube + Docker driver)..."

# ==============================
# 1️⃣ Iniciar Minikube
# ==============================
if ! minikube status >/dev/null 2>&1; then
  echo "🟡 Iniciando Minikube..."
  minikube start
else
  echo "✅ Minikube ya está en ejecución."
fi

# ==============================
# 2️⃣ Instalar Knative Serving si no existe
# ==============================
if ! kubectl get ns ${KNATIVE_NS} >/dev/null 2>&1; then
  echo "🟢 Instalando Knative Serving..."
  kubectl apply -f https://github.com/knative/serving/releases/latest/download/serving-crds.yaml
  kubectl apply -f https://github.com/knative/serving/releases/latest/download/serving-core.yaml
fi

# ==============================
# 3️⃣ Instalar Kourier como Ingress
# ==============================
if ! kubectl get ns ${KOURIER_NS} >/dev/null 2>&1; then
  echo "🟢 Instalando Kourier..."
  kubectl apply -f https://github.com/knative/net-kourier/releases/latest/download/kourier.yaml
  kubectl patch configmap/config-network \
    --namespace ${KNATIVE_NS} \
    --type merge \
    --patch '{"data":{"ingress.class":"kourier.ingress.networking.knative.dev"}}'
fi

# Esperar hasta que los pods estén listos
echo "⏳ Esperando a que Knative y Kourier estén listos..."
kubectl wait pod --for=condition=Ready -n ${KNATIVE_NS} --all --timeout=180s || true
kubectl wait pod --for=condition=Ready -n ${KOURIER_NS} --all --timeout=180s || true

# ==============================
# 4️⃣ Configurar dominio local
# ==============================
echo "🌍 Configurando dominio example.com para Knative..."
kubectl patch configmap/config-domain \
  --namespace ${KNATIVE_NS} \
  --type merge \
  --patch '{"data":{"example.com":""}}'

# ==============================
# 5️⃣ Crear Knative Service para la app
# ==============================
echo "🧱 Desplegando Knative Service ${APP_NAME}..."
cat <<EOF | kubectl apply -f -
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: ${APP_NAME}
  namespace: ${NAMESPACE}
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "1"
    spec:
      containers:
        - image: ${APP_IMAGE}
          ports:
            - containerPort: 5000
EOF

echo "⏳ Esperando a que el servicio esté listo..."
kubectl wait kservice/${APP_NAME} --for=condition=Ready --timeout=120s

# ==============================
# 6️⃣ Mostrar URL y abrir proxy
# ==============================
SERVICE_URL=$(kubectl get kservice ${APP_NAME} -o jsonpath='{.status.url}')
echo "✅ Servicio desplegado: ${SERVICE_URL}"
echo "🌐 Abriendo proxy a Kourier con minikube service..."
echo "📍 Usa este comando para acceder:"
echo "    curl -H \"Host: ${APP_NAME}.default.example.com\" http://127.0.0.1:<PUERTO>"
echo ""
minikube service kourier -n ${KOURIER_NS}
