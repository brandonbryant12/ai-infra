# LiteLLM Proxy Gateway Deployment Guide

This guide provides instructions for deploying LiteLLM proxy gateway without a database, configured to connect to your OpenWebUI instance.

## Prerequisites
- Python 3.8+ (for local Python deployment)
- Docker (for Docker deployment)
- Kubernetes cluster with Helm (for Helm deployment)
- Your OpenWebUI API endpoint: `http://myinstance.com/api`
- Your OpenWebUI API token

## 1. Python Local Setup

### Step 1: Install LiteLLM
```bash
pip install 'litellm[proxy]'
```

### Step 2: Create Configuration File
Create a file named `litellm_config.yaml`:

```yaml
model_list:
  - model_name: openwebui-default
    litellm_params:
      model: openai/openwebui-model
      api_base: http://myinstance.com/api
      api_key: your-openwebui-api-token
      
  # Add more models as needed
  - model_name: openwebui-gpt4
    litellm_params:
      model: openai/gpt-4
      api_base: http://myinstance.com/api
      api_key: your-openwebui-api-token

# Optional: Set default timeout
litellm_settings:
  drop_params: True
  set_verbose: False
```

### Step 3: Set Environment Variables (Optional)
If you prefer to use environment variables for sensitive data:

```bash
export OPENWEBUI_API_KEY="your-openwebui-api-token"
export OPENWEBUI_API_BASE="http://myinstance.com/api"
```

Then update your config to reference these:
```yaml
model_list:
  - model_name: openwebui-default
    litellm_params:
      model: openai/openwebui-model
      api_base: os.environ/OPENWEBUI_API_BASE
      api_key: os.environ/OPENWEBUI_API_KEY
```

### Step 4: Start the Proxy
```bash
litellm --config ./litellm_config.yaml --port 4000
```

### Step 5: Test the Connection
```bash
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "openwebui-default",
    "messages": [{"role": "user", "content": "Hello, how are you?"}]
  }'
```

## 2. Docker Local Setup

### Step 1: Create Configuration File
Create the same `litellm_config.yaml` as above.

### Step 2: Create .env File (Optional)
Create a `.env` file for environment variables:

```bash
OPENWEBUI_API_KEY=your-openwebui-api-token
OPENWEBUI_API_BASE=http://myinstance.com/api
```

### Step 3: Run with Docker
```bash
docker run \
  -v $(pwd)/litellm_config.yaml:/app/config.yaml \
  -e OPENWEBUI_API_KEY=$OPENWEBUI_API_KEY \
  -e OPENWEBUI_API_BASE=$OPENWEBUI_API_BASE \
  -p 4000:4000 \
  ghcr.io/berriai/litellm:main-latest \
  --config /app/config.yaml --detailed_debug
```

### Step 4: Docker Compose Alternative
Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  litellm:
    image: ghcr.io/berriai/litellm:main-latest
    ports:
      - "4000:4000"
    volumes:
      - ./litellm_config.yaml:/app/config.yaml
    environment:
      - OPENWEBUI_API_KEY=${OPENWEBUI_API_KEY}
      - OPENWEBUI_API_BASE=${OPENWEBUI_API_BASE}
    command: --config /app/config.yaml --detailed_debug
```

Run with:
```bash
docker-compose up -d
```

## 3. Custom Docker Build (Clean Minimal Image)

### Step 1: Create Dockerfile
Create a minimal `Dockerfile`:

```dockerfile
# Use official Python slim image for minimal size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install only the necessary dependencies
RUN pip install --no-cache-dir 'litellm[proxy]' && \
    # Clean up pip cache and unnecessary files
    pip cache purge && \
    rm -rf /root/.cache/pip/* && \
    # Remove unnecessary Python files
    find /usr/local/lib/python3.11 -name '__pycache__' -type d -exec rm -rf {} + && \
    find /usr/local/lib/python3.11 -name '*.pyc' -delete && \
    # Remove test files and docs
    find /usr/local/lib/python3.11 -name 'test*' -type d -exec rm -rf {} + && \
    find /usr/local/lib/python3.11 -name 'tests' -type d -exec rm -rf {} + && \
    # Clean apt cache
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 litellm && chown -R litellm:litellm /app
USER litellm

# Expose port
EXPOSE 4000

# Set entrypoint
ENTRYPOINT ["litellm"]
CMD ["--port", "4000"]
```

### Step 2: Multi-stage Build Alternative (Even Smaller)
For an even cleaner build, use multi-stage:

```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install litellm
RUN pip install --no-cache-dir 'litellm[proxy]'

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user
RUN useradd -m -u 1000 litellm && chown -R litellm:litellm /app
USER litellm

EXPOSE 4000

ENTRYPOINT ["litellm"]
CMD ["--port", "4000"]
```

### Step 3: Alpine-based Alternative (Smallest)
For the absolute minimal image:

```dockerfile
FROM python:3.11-alpine

WORKDIR /app

# Install build dependencies temporarily
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    python3-dev \
    && pip install --no-cache-dir 'litellm[proxy]' \
    && apk del .build-deps \
    && rm -rf /root/.cache/pip/*

# Create non-root user
RUN adduser -D -u 1000 litellm && chown -R litellm:litellm /app
USER litellm

EXPOSE 4000

ENTRYPOINT ["litellm"]
CMD ["--port", "4000"]
```

### Step 4: Build the Image
```bash
# Choose one of the Dockerfiles above and build
docker build -t litellm-proxy:custom .

# For specific architecture (e.g., arm64 for M1 Macs)
docker buildx build --platform linux/amd64,linux/arm64 -t litellm-proxy:custom .
```

### Step 5: Run Your Custom Image
```bash
# Run with mounted config
docker run -d \
  --name litellm-proxy \
  -v $(pwd)/litellm_config.yaml:/app/config.yaml:ro \
  -p 4000:4000 \
  litellm-proxy:custom \
  --config /app/config.yaml

# Run with environment variables only (no mounted files)
docker run -d \
  --name litellm-proxy \
  -e OPENWEBUI_API_KEY="your-api-key" \
  -e OPENWEBUI_API_BASE="http://myinstance.com/api" \
  -p 4000:4000 \
  litellm-proxy:custom \
  --model openai/openwebui-model \
  --api_base http://myinstance.com/api \
  --api_key "$OPENWEBUI_API_KEY"
```

### Step 6: Docker Compose with Custom Build
Create `docker-compose.yml` with build configuration:

```yaml
version: '3.8'

services:
  litellm:
    build:
      context: .
      dockerfile: Dockerfile
    image: litellm-proxy:custom
    container_name: litellm-proxy
    ports:
      - "4000:4000"
    volumes:
      - ./litellm_config.yaml:/app/config.yaml:ro
    environment:
      - OPENWEBUI_API_KEY=${OPENWEBUI_API_KEY}
      - OPENWEBUI_API_BASE=${OPENWEBUI_API_BASE}
    command: --config /app/config.yaml
    restart: unless-stopped
    # Security options
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
```

### Optimization Tips:

1. **Use .dockerignore**:
```
# .dockerignore
*.md
*.log
.git
.gitignore
.env
__pycache__
*.pyc
.pytest_cache
.coverage
htmlcov/
dist/
build/
*.egg-info/
```

2. **Security Hardening**:
```dockerfile
# Add to Dockerfile for additional security
# Disable pip version check
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
# Don't write .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
# Don't buffer stdout/stderr
ENV PYTHONUNBUFFERED=1
```

3. **Health Check**:
```dockerfile
# Add to Dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD ["python", "-c", "import requests; requests.get('http://localhost:4000/health')"]
```

### Image Size Comparison:
- Official image: ~500-800MB
- Custom slim image: ~150-250MB  
- Multi-stage build: ~120-180MB
- Alpine-based: ~80-120MB

## 4. Helm Chart Deployment

### Step 1: Create values.yaml
Create a `values.yaml` file:

```yaml
replicaCount: 1

image:
  repository: ghcr.io/berriai/litellm
  tag: main-latest
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 4000

ingress:
  enabled: true
  className: nginx
  annotations: {}
  hosts:
    - host: litellm.yourdomain.com
      paths:
        - path: /
          pathType: Prefix
  tls: []

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi

autoscaling:
  enabled: false
  minReplicas: 1
  maxReplicas: 3
  targetCPUUtilizationPercentage: 80

# LiteLLM Configuration
config:
  model_list:
    - model_name: openwebui-default
      litellm_params:
        model: openai/openwebui-model
        api_base: http://myinstance.com/api
        api_key: ${OPENWEBUI_API_KEY}
    
    - model_name: openwebui-gpt4
      litellm_params:
        model: openai/gpt-4
        api_base: http://myinstance.com/api
        api_key: ${OPENWEBUI_API_KEY}
  
  litellm_settings:
    drop_params: true
    set_verbose: false

# Environment variables
env:
  - name: OPENWEBUI_API_KEY
    valueFrom:
      secretKeyRef:
        name: litellm-secrets
        key: openwebui-api-key
```

### Step 2: Create Kubernetes Secret
```bash
kubectl create secret generic litellm-secrets \
  --from-literal=openwebui-api-key=your-openwebui-api-token \
  -n your-namespace
```

### Step 3: Create Helm Chart Structure
Create the following directory structure:

```
litellm-chart/
├── Chart.yaml
├── values.yaml
└── templates/
    ├── deployment.yaml
    ├── service.yaml
    ├── configmap.yaml
    └── ingress.yaml
```

### Step 4: Chart.yaml
```yaml
apiVersion: v2
name: litellm-proxy
description: LiteLLM Proxy Gateway
type: application
version: 0.1.0
appVersion: "main-latest"
```

### Step 5: templates/configmap.yaml
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "litellm-proxy.fullname" . }}-config
data:
  config.yaml: |
{{ .Values.config | toYaml | indent 4 }}
```

### Step 6: templates/deployment.yaml
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "litellm-proxy.fullname" . }}
  labels:
    {{- include "litellm-proxy.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "litellm-proxy.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "litellm-proxy.selectorLabels" . | nindent 8 }}
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: 4000
              protocol: TCP
          env:
            {{- toYaml .Values.env | nindent 12 }}
          volumeMounts:
            - name: config
              mountPath: /app/config.yaml
              subPath: config.yaml
          command:
            - "litellm"
            - "--config"
            - "/app/config.yaml"
            - "--port"
            - "4000"
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
      volumes:
        - name: config
          configMap:
            name: {{ include "litellm-proxy.fullname" . }}-config
```

### Step 7: Deploy with Helm
```bash
# Install
helm install litellm-proxy ./litellm-chart -n your-namespace

# Upgrade with new configuration
helm upgrade litellm-proxy ./litellm-chart -n your-namespace

# Check status
kubectl get pods -n your-namespace
kubectl logs -n your-namespace deployment/litellm-proxy
```

## Adding More Connections

To add more API connections, simply update the `model_list` section in your configuration:

```yaml
model_list:
  # OpenWebUI Models
  - model_name: openwebui-default
    litellm_params:
      model: openai/openwebui-model
      api_base: http://myinstance.com/api
      api_key: your-openwebui-api-token
  
  # OpenAI Direct
  - model_name: gpt-4
    litellm_params:
      model: gpt-4
      api_key: sk-your-openai-key
  
  # Azure OpenAI
  - model_name: azure-gpt-4
    litellm_params:
      model: azure/your-deployment-name
      api_base: https://your-resource.openai.azure.com/
      api_key: your-azure-key
      api_version: "2024-02-15-preview"
  
  # Anthropic
  - model_name: claude-3
    litellm_params:
      model: claude-3-opus-20240229
      api_key: your-anthropic-key
  
  # Custom OpenAI-compatible endpoint
  - model_name: local-llm
    litellm_params:
      model: openai/llama-2-7b
      api_base: http://localhost:8080
      api_key: dummy-key
```

## Testing Your Deployment

### Test endpoint availability:
```bash
curl http://localhost:4000/health
```

### List available models:
```bash
curl http://localhost:4000/v1/models
```

### Make a chat completion request:
```bash
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "openwebui-default",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Hello!"}
    ]
  }'
```

## Troubleshooting

1. **Connection Refused**: Ensure your OpenWebUI instance is accessible from where LiteLLM is running
2. **Authentication Failed**: Verify your API token is correct
3. **Model Not Found**: Check that the model name in your request matches the `model_name` in your config
4. **Timeout Issues**: Add timeout configuration:
   ```yaml
   litellm_settings:
     request_timeout: 600
     stream_timeout: 60
   ```

## Production Considerations

1. **Enable Health Checks**: Add to your config:
   ```yaml
   general_settings:
     health_check_interval: 300
   ```

2. **Set Rate Limits**: Add to model config:
   ```yaml
   - model_name: openwebui-default
     litellm_params:
       # ... existing params ...
       rpm: 100  # requests per minute
       tpm: 100000  # tokens per minute
   ```

3. **Enable Logging**: For production debugging:
   ```yaml
   litellm_settings:
     set_verbose: true
     log_raw_request_response: true
   ```