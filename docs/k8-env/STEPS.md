# Configuración de entorno Kubernetes con Knative en Ubuntu (Linux)
## Requisitos previos
### Herramientas básicas
`sudo apt update`

`sudo apt install -y curl apt-transport-https ca-certificates gnupg lsb-release`

### Docker
`sudo apt install -y docker.io`

`sudo usermod -aG docker $USER`

`newgrp docker`

### kubectl
`curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"`

`sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl`

### Minikube
`curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64`

`sudo install minikube-linux-amd64 /usr/local/bin/minikube`

## Pasos
### Crear el clúster Kubernetes
`minikube start --driver=docker`

### Verificar nodes
`kubectl get nodes`

### Comprobar clústers
`kubectl config get-contexts`

### Comprobar namespaces
`kubectl get ns`

### Comprobar pods
`kubectl get pods -n ...`

### Instalar Knative Serving
#### Instalar el CRD y los componentes base
`kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.15.0/serving-crds.yaml`

`kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.15.0/serving-core.yaml`

#### Instalar Kourier (network layer)
`kubectl apply -f https://github.com/knative/net-kourier/releases/download/knative-v1.15.0/kourier.yaml`

`kubectl patch configmap/config-network -n knative-serving -p '{"data":{"ingress-class":"kourier.ingress.networking.knative.dev"}}'`

#### Exponer el servicio ingress
`kubectl --namespace kourier-system get service kourier`

`minikube tunnel &`

### Verificar Knative
`kubectl get pods -n knative-serving`

### Desplegar dummy-python-app
En la carpeta del proyecto:
`docker build -t $NAME .`

`minikube image load $NAME`

### Crear servicio Knative
#### Aplicar el manifiesto
Con el service.yaml creado y en la carpeta del proyecto:
`kubectl apply -f service.yaml`

#### Verificar el estado
kubectl get ksvc

















kubectl apply -f service.yaml
Warning: Kubernetes default value is insecure, Knative may default this to secure in a future release: spec.template.spec.containers[0].securityContext.allowPrivilegeEscalation, spec.template.spec.containers[0].securityContext.capabilities, spec.template.spec.containers[0].securityContext.runAsNonRoot, spec.template.spec.containers[0].securityContext.seccompProfile
service.serving.knative.dev/dummy-python-app created


