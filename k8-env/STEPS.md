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
minikube start --driver=docker

### Comprobar clústers
kubectl config get-contexts

### 

