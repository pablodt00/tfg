#!/bin/bash

set -e

echo "🚀 Setting up local Kubernetes with Knative..."

if ! command -v kind &> /dev/null; then
    echo "❌ kind is not installed. Please install it first:"
    echo "   curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64"
    echo "   chmod +x ./kind"
    echo "   sudo mv ./kind /usr/local/bin/kind"
    exit 1
fi

if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed. Please install it first:"
    echo "   https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/"
    exit 1
fi

CLUSTER_NAME="tfg-knative-local"

if kind get clusters | grep -q "^${CLUSTER_NAME}$"; then
    echo "⚠️  Cluster ${CLUSTER_NAME} already exists. Delete it? (y/n)"
    read -r response
    if [[ "$response" == "y" ]]; then
        echo "🗑️  Deleting existing cluster..."
        kind delete cluster --name ${CLUSTER_NAME}
    else
        echo "ℹ️  Using existing cluster"
        exit 0
    fi
fi

echo "📦 Creating kind cluster..."
kind create cluster --name ${CLUSTER_NAME} --config kubernetes/kind-config.yaml

echo "📥 Installing Knative Serving..."
kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.12.0/serving-crds.yaml
kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.12.0/serving-core.yaml

echo "🌐 Installing Kourier..."
kubectl apply -f https://github.com/knative/net-kourier/releases/download/knative-v1.12.0/kourier.yaml

kubectl patch configmap/config-network \
  --namespace knative-serving \
  --type merge \
  --patch '{"data":{"ingress-class":"kourier.ingress.networking.knative.dev"}}'

echo "🔧 Configuring DNS..."
kubectl apply -f kubernetes/knative-dns.yaml

echo "⏳ Waiting for Knative to be ready..."
kubectl wait --for=condition=Available deployment --all -n knative-serving --timeout=300s
kubectl wait --for=condition=Available deployment --all -n kourier-system --timeout=300s

echo "✅ Knative setup complete!"
echo ""
echo "📝 Useful commands:"
echo "   kubectl get ksvc                    # List Knative services"
echo "   kubectl get pods -n knative-serving # Check Knative pods"
echo "   kind delete cluster --name ${CLUSTER_NAME}  # Delete cluster"
echo ""
echo "🚀 You can now deploy services with: kubectl apply -f kubernetes/services/"
