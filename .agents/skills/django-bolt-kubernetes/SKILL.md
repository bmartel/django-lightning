---
name: django-bolt-kubernetes
description: Enterprise Kubernetes deployment manifests, HPA, Ingress, cert-manager Let's Encrypt TLS termination, probes, and secret management for django-bolt applications.
compatibility: Agentic coding assistants building web applications with django-bolt.
metadata:
  category: kubernetes
  tags: [kubernetes, k8s, deployment, hpa, ingress, probes, cert-manager, letsencrypt, ssl, caddy, django-bolt]
---

# Django-Bolt Kubernetes Infrastructure

## Key Kubernetes Requirements

- **Command Entrypoint**: Container specification must invoke `["python", "manage.py", "runbolt", "--host", "0.0.0.0", "--port", "8000", "--processes", "4"]`.
- **Health Probes**: Target `/health` for both `livenessProbe` and `readinessProbe`.
- **Autoscaling (HPA)**: Scale between 3 and 20+ replicas based on CPU (75%) and memory (80%) utilization.
- **Ingress Timeouts & Streaming**: Configure ingress proxy read/send timeouts to 3600s and disable proxy buffering (`proxy-buffering: "off"`) for SSE and WebSocket support.
- **SSL / TLS Let's Encrypt**: Use `cert-manager` with `ClusterIssuer` (`letsencrypt-prod`) or deploy the standalone `caddy-ingress.yaml` gateway.

## Production Ingress with Cert-Manager Let's Encrypt

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@example.com
    privateKeySecretRef:
      name: letsencrypt-prod-account-key
    solvers:
    - http01:
        ingress:
          class: nginx
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: django-lightning-ingress
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "3600"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "3600"
    nginx.ingress.kubernetes.io/proxy-buffering: "off"
spec:
  tls:
  - hosts:
    - api.example.com
    secretName: django-lightning-tls
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: django-lightning-service
            port:
              number: 80
```

## Standalone Caddy Gateway Deployment in Kubernetes

For setups without external Ingress Controllers, apply `k8s/caddy-ingress.yaml` to run Caddy directly as a Kubernetes LoadBalancer proxy with persistent TLS storage via PVC (`caddy-data-pvc`).

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
