# Deployment Targets (Beyond Docker)

This guide documents non-Docker deployment options for the adapter.

## Bare Metal (Python Service)

Prerequisites:
- Python 3.12+
- `pip install -r requirements.txt`

Pros:
- Simple to debug
- Lowest operational overhead

Cons:
- Manual process management
- Requires host-level security hardening

## Managed Cloud VM (AWS/GCP/Azure)

Prerequisites:
- VM with Python 3.12+
- Ingress/Firewall rules for the service port

Pros:
- Standard infrastructure
- Easier networking than serverless

Cons:
- You manage OS patching and scaling

## Kubernetes

Prerequisites:
- Container image and K8s cluster
- Service/Ingress configuration

Pros:
- Scales cleanly
- Standardized deployment pipelines

Cons:
- Higher operational complexity

## Serverless (Functions/Containers)

Prerequisites:
- Provider that supports long-running HTTP services
- Cold start considerations

Pros:
- Pay-per-use
- Minimal host management

Cons:
- Latency variability
- Limits on request duration and concurrency
