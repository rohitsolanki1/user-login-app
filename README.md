# user-login-app — README

**One-stop guide** to build, run, debug and operate the `user-login-app` on an **on-prem MicroK8s** cluster.
This README is written as a step-by-step operational playbook — follow the sections in order.

---

## Table of contents

1. [Overview & architecture](#overview--architecture)
2. [Prerequisites](#prerequisites)
3. [Repo layout](#repo-layout)
4. [Quick start — bootstrap MicroK8s & registry](#quick-start--bootstrap-microk8s--registry)
5. [Build images (manual) & push to local registry](#build-images-manual--push-to-local-registry)
6. [Apply Kubernetes manifests](#apply-kubernetes-manifests)
7. [Ingress / Access from LAN (recommended)](#ingress--access-from-lan-recommended)
8. [Jenkins CI/CD (recommended pipeline)](#jenkins-cicd-recommended-pipeline)
9. [Database exploration (Postgres)](#database-exploration-postgres)
10. [Debugging & common fixes](#debugging--common-fixes)
11. [Force updates & deployment patterns](#force-updates--deployment-patterns)
12. [Load testing basics](#load-testing-basics)
13. [Monitoring & metrics (CPU/memory/traffic)](#monitoring--metrics-cpu-memory-traffic)
14. [Security & production notes](#security--production-notes)
15. [Next improvements / checklist](#next-improvements--checklist)

---

# Overview & architecture

* **Frontend**: static HTML + JS served by nginx (login + register forms).
* **Backend**: Flask REST API (`/api/register`, `/api/login`, `/api/health`) with JWT.
* **DB**: PostgreSQL (PVC).
* **Kubernetes**: MicroK8s (namespace `user-login-app`).
* **Registry**: local Docker registry (example: `localhost:32100`).
* **CI/CD**: Jenkins builds images → pushes to local registry → `kubectl apply` + rollout restart.

---

# Prerequisites

* Linux server (or WSL2) with MicroK8s installed and enough resources.
* `microk8s` CLI available and you can run `microk8s kubectl`.
* Docker installed on the machine that builds images (or Jenkins agent).
* (Optional) Jenkins installed on same host or with access to registry & kubeconfig.
* Replace example IPs/ports with your own in commands below.

---

# Repo layout

```
user-login-app/
├─ frontend/
│  ├─ dist/index.html
│  └─ Dockerfile
├─ backend/
│  ├─ app.py
│  ├─ requirements.txt
│  └─ Dockerfile
├─ k8s/
│  ├─ namespace-secret.yaml
│  ├─ postgres.yaml
│  ├─ backend.yaml
│  ├─ backend-service.yaml
│  ├─ frontend.yaml
│  ├─ frontend-service.yaml
│  └─ ingress.yaml
├─ Jenkinsfile
└─ README.md
```

---

# Quick start — bootstrap MicroK8s & registry

1. Install/enable MicroK8s (if not already)

```bash
sudo snap install microk8s --classic --channel=1.30/stable
sudo usermod -a -G microk8s $USER
newgrp microk8s
```

2. Enable required addons (DNS, storage, ingress, metrics, registry, dashboard)

```bash
microk8s enable dns storage ingress registry metrics-server dashboard
alias k='microk8s kubectl'
```

3. Create namespace and secret (update values before applying)

```bash
k apply -f k8s/namespace-secret.yaml
```

> **Registry note:** MicroK8s registry usually listens at `localhost:32000`. Example for a dedicated registry:

```bash
docker run -d -p 32100:5000 --restart=always --name user-login-app-registry registry:2
```

---

# Build images (manual) & push to local registry

From repo root:

```bash
cd backend
docker build -t localhost:32100/user-login-app-backend:latest .
docker push localhost:32100/user-login-app-backend:latest

cd ../frontend
docker build -t localhost:32100/user-login-app-frontend:latest .
docker push localhost:32100/user-login-app-frontend:latest
```

---

# Apply Kubernetes manifests

```bash
k apply -f k8s/ -n user-login-app
k get all -n user-login-app
```

Force rollout for new images:

```bash
k rollout restart deployment/backend -n user-login-app
k rollout restart deployment/frontend -n user-login-app
```

Check logs:

```bash
k logs -l app=backend -n user-login-app --tail=100
```

---

# Ingress / Access from LAN (recommended)

1. Edit `k8s/ingress.yaml` hostname.
2. Apply: `k apply -f k8s/ingress.yaml -n user-login-app`
3. Add entry in `/etc/hosts`:

```
<node-ip>  user-login-app.local
```

4. Open `http://user-login-app.local`

---

# Jenkins CI/CD (recommended pipeline)

Example `Jenkinsfile`:

```groovy
pipeline {
  agent any
  environment {
    REGISTRY = "localhost:32100"
    PROJECT = "user-login-app"
    BACKEND_IMAGE = "${REGISTRY}/${PROJECT}-backend:latest"
    FRONTEND_IMAGE = "${REGISTRY}/${PROJECT}-frontend:latest"
    NAMESPACE = "user-login-app"
  }
  stages {
    stage('Checkout') { steps { checkout scm } }
    stage('Build') {
      steps {
        sh "docker build -t ${BACKEND_IMAGE} backend"
        sh "docker build -t ${FRONTEND_IMAGE} frontend"
      }
    }
    stage('Push') {
      steps {
        sh "docker push ${BACKEND_IMAGE}"
        sh "docker push ${FRONTEND_IMAGE}"
      }
    }
    stage('Deploy') {
      steps {
        sh "microk8s kubectl apply -f k8s/ -n ${NAMESPACE}"
        sh "microk8s kubectl rollout restart deployment/backend -n ${NAMESPACE}"
        sh "microk8s kubectl rollout restart deployment/frontend -n ${NAMESPACE}"
      }
    }
  }
}
```

---

# Database exploration (Postgres)

```bash
k exec -it deploy/postgres -n user-login-app -- bash
psql -U appuser -d appdb

db=# \dt
SELECT * FROM "user";
\q
```

---

# Debugging & common fixes

* Ensure `Flask-SQLAlchemy` in Dockerfile `requirements.txt`.
* NodePort lowercase: `nodePort`.
* Unexpected HTML (frontend 404): check fetch URL matches backend route.
* CORS: use `flask_cors.CORS(app)` if needed.
* Force image update: `rollout restart` + `imagePullPolicy: Always`.

---

# Force updates & deployment patterns

* Dev: `latest` + `rollout restart`
* Prod: tag images + update Deployment + probes.

---

# Load testing basics

Install `hey` or `k6`:

```bash
hey -n 1000 -c 50 http://user-login-app.local/api/health
```

---

# Monitoring & metrics (CPU/memory/traffic)

```bash
microk8s enable metrics-server
k top pod -n user-login-app
k top node
microk8s enable observability
microk8s dashboard-proxy
```

---

# Security & production notes

* Use secrets properly, TLS with cert-manager, backups, network policies.

---

# Next improvements / checklist

* DB migration with Alembic, rate-limiting, Helm/Kustomize, e2e tests, Prometheus alerts.

---

# Useful commands

```bash
alias k='microk8s kubectl'
k get all -n user-login-app
k describe deploy backend -n user-login-app
k logs -l app=backend -n user-login-app --tail=200
k rollout restart deployment/backend -n user-login-app
k exec -it deploy/postgres -n user-login-app -- bash
```
