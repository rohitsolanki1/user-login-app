# user-login-app

This repository contains an on-prem demo stack for a simple user login website:
- Frontend: static login page served by nginx
- Backend: Flask REST API with JWT auth
- Database: Postgres (PVC)
- CI/CD: Jenkinsfile to build Docker images and deploy to MicroK8s

Quick steps:
1. Enable microk8s addons: `microk8s enable dns storage ingress registry`
2. Apply k8s manifests: `microk8s kubectl apply -f k8s/`
3. Build & push images to local registry `localhost:32000`:
   - `docker build -t localhost:32000/user-login-app/backend:latest ./backend`
   - `docker push localhost:32000/user-login-app/backend:latest`
   - `docker build -t localhost:32000/user-login-app/frontend:latest ./frontend`
   - `docker push localhost:32000/user-login-app/frontend:latest`
4. Restart deployments:
   - `microk8s kubectl -n user-login-app rollout restart deployment/backend`
   - `microk8s kubectl -n user-login-app rollout restart deployment/frontend`
5. Add `/etc/hosts` entry: `127.0.0.1 user-login-app.local` (or node IP)
6. Open http://user-login-app.local

Notes:
- Replace secrets in k8s/secrets.yaml before production.
- This is a demo; passwords are stored in plaintext for simplicity. Use bcrypt in production.
