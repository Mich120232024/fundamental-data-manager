# FX Options Pricing Engine - Kubernetes Deployment

## Microservice Architecture

The pricing engine is designed as a standalone microservice that can serve multiple frontend applications:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  GZC Intel App  │     │ Bloomberg Vol   │     │ Other Trading   │
│    (Main App)   │     │   Component     │     │     Apps        │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                         │
         └───────────────────────┴─────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   Kubernetes Cluster    │
                    │  ┌──────────────────┐  │
                    │  │ Pricing Service  │  │
                    │  │   (3 replicas)   │  │
                    │  └──────────────────┘  │
                    │           │            │
                    │  ┌────────▼────────┐  │
                    │  │ Bloomberg Cache  │  │
                    │  │     (Redis)      │  │
                    │  └─────────────────┘  │
                    └────────────────────────┘
```

## Kubernetes Resources

### 1. Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fx-options-pricing-engine
  namespace: gzc-intel
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fx-pricing-engine
  template:
    metadata:
      labels:
        app: fx-pricing-engine
    spec:
      containers:
      - name: pricing-engine
        image: gzcacr.azurecr.io/fx-pricing-engine:latest
        ports:
        - containerPort: 8001
        env:
        - name: BLOOMBERG_API_URL
          value: "http://bloomberg-api-service:8080"
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: redis-credentials
              key: connection-string
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 30
          periodSeconds: 10
```

### 2. Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: fx-pricing-engine-service
  namespace: gzc-intel
spec:
  selector:
    app: fx-pricing-engine
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8001
  type: ClusterIP
```

### 3. Ingress
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: fx-pricing-engine-ingress
  namespace: gzc-intel
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: pricing.gzc-intel.internal
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: fx-pricing-engine-service
            port:
              number: 80
```

### 4. Horizontal Pod Autoscaler
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: fx-pricing-engine-hpa
  namespace: gzc-intel
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: fx-options-pricing-engine
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

# Copy application
COPY . .

# Run as non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

## Integration Points

### 1. GZC Intel App
```javascript
// In GZC Intel App component registry
export const OptionsPricingWidget = {
  name: 'FXOptionsPricing',
  version: '1.0.0',
  apiEndpoint: process.env.REACT_APP_PRICING_API || 'https://pricing.gzc-intel.internal',
  component: lazy(() => import('./OptionsPricingWidget'))
}
```

### 2. Bloomberg Volatility Component
```typescript
// Add to existing bloomberg.ts
export const pricingAPI = {
  async priceOption(params: OptionParams): Promise<PricingResult> {
    const response = await fetch(`${PRICING_API_URL}/api/pricing/vanilla`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    })
    return response.json()
  }
}
```

### 3. Other Trading Apps
Any app in the GZC ecosystem can call the pricing API directly.

## Caching Strategy

Using Redis for:
1. **Market Data Cache** - 1 minute TTL for spot rates
2. **Forward Points Cache** - 5 minute TTL
3. **Volatility Surface Cache** - 1 minute TTL
4. **Pricing Results Cache** - 10 second TTL for identical requests

## Monitoring

### Prometheus Metrics
- `pricing_requests_total` - Total pricing requests
- `pricing_duration_seconds` - Pricing calculation time
- `bloomberg_api_calls_total` - Bloomberg API calls
- `cache_hit_ratio` - Redis cache effectiveness

### Grafana Dashboard
- Real-time pricing volume
- Latency percentiles (p50, p95, p99)
- Error rates by endpoint
- Cache hit rates

## Security

1. **API Authentication** - Azure AD tokens required
2. **Rate Limiting** - 100 requests/minute per client
3. **Input Validation** - Strict parameter validation
4. **Network Policies** - Only allow traffic from frontend services

## Deployment Process

```bash
# Build and push Docker image
docker build -t gzcacr.azurecr.io/fx-pricing-engine:latest .
docker push gzcacr.azurecr.io/fx-pricing-engine:latest

# Deploy to Kubernetes
kubectl apply -f k8s/

# Check deployment status
kubectl rollout status deployment/fx-options-pricing-engine -n gzc-intel
```

This microservice architecture ensures:
- High availability across multiple frontends
- Scalability based on demand
- Centralized pricing logic
- Consistent calculations across all apps