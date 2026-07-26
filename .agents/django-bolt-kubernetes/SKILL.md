---
name: django-bolt-kubernetes
description: Enterprise Kubernetes deployment manifests, HPA, Ingress, probes, and secret management for django-bolt applications.
compatibility: Agentic coding assistants building web applications with django-bolt.
metadata:
  category: kubernetes
  tags: [kubernetes, k8s, deployment, hpa, ingress, probes, django-bolt]
---

# Django-Bolt Kubernetes Infrastructure

## Key Kubernetes Requirements

- **Command Entrypoint**: Container specification must invoke `["python", "manage.py", "runbolt", "--host", "0.0.0.0", "--port", "8000", "--processes", "4"]`.
- **Health Probes**: Target `/health` for both `livenessProbe` and `readinessProbe`.
- **Autoscaling (HPA)**: Scale between 3 and 20+ replicas based on CPU (75%) and memory (80%) utilization.
- **Ingress Timeouts**: Configure NGINX ingress proxy read/send timeouts to 3600s for SSE and WebSocket support.

## Key Manifest Excerpt

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: django-lightning
spec:
  replicas: 3
  selector:
    matchLabels:
      app: django-lightning
  template:
    metadata:
      labels:
        app: django-lightning
    spec:
      containers:
      - name: api
        image: django-lightning:latest
        command: ["python", "manage.py", "runbolt", "--host", "0.0.0.0", "--port", "8000", "--processes", "4"]
        ports:
        - containerPort: 8000
          name: http
        livenessProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 5


## Zero-Downtime Migration Strategy in Kubernetes

1. **Pre-rollout Synchronous DDL Schema Migration**:
   - Run the dedicated Kubernetes Migration Job before triggering deployment updates:
     `kubectl apply -f k8s/job-migration.yaml`
2. **Rolling Update Deployment**:
   - Apply deployment changes with zero unavailable pods (`maxUnavailable: 0`):
     `kubectl apply -f k8s/deployment.yaml`
3. **Post-rollout Asynchronous DML Data Migration**:
   - Enqueue background data backfills via SAQ background worker:
     `uv run manage.py async_migrate --enqueue <migration_name>`

```
