# LiteLLM Custom Docker Build

Build your own minimal LiteLLM Docker image for optimal size and security.

## Why Custom Build?

- **Smaller Size**: 80-250MB vs 500-800MB official image
- **Better Security**: Non-root user, minimal attack surface
- **Customization**: Add only what you need
- **Multi-architecture**: Build for specific platforms

## Build Options

### 1. Standard Slim Build

**Size**: ~150-250MB

Create `Dockerfile`:

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

### 2. Multi-Stage Build

**Size**: ~120-180MB

Create `Dockerfile.multistage`:

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

### 3. Alpine Linux Build

**Size**: ~80-120MB

Create `Dockerfile.alpine`:

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

### 4. Security-Hardened Build

**Size**: ~150-200MB

Create `Dockerfile.secure`:

```dockerfile
# Multi-stage security-focused build
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies
RUN pip install --no-cache-dir 'litellm[proxy]' requests

# Runtime stage
FROM python:3.11-slim

# Install security updates
RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Security settings
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

# Create app directory with restricted permissions
RUN mkdir -p /app && chmod 755 /app

# Create non-root user
RUN groupadd -r litellm && useradd -r -g litellm -u 1000 litellm

# Set ownership
RUN chown -R litellm:litellm /app

WORKDIR /app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:4000/health')" || exit 1

USER litellm

EXPOSE 4000

ENTRYPOINT ["litellm"]
CMD ["--port", "4000"]
```

## Build Process

### Basic Build

```bash
# Choose your Dockerfile
docker build -t litellm-proxy:custom -f Dockerfile .

# Build with build arguments
docker build \
  --build-arg PYTHON_VERSION=3.11 \
  -t litellm-proxy:custom .
```

### Multi-Architecture Build

```bash
# Setup buildx
docker buildx create --name multiarch --use

# Build for multiple platforms
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t litellm-proxy:custom \
  --push .
```

### Build with Cache

```bash
# Use BuildKit for better caching
DOCKER_BUILDKIT=1 docker build \
  --cache-from litellm-proxy:custom \
  -t litellm-proxy:custom .
```

## Supporting Files

### .dockerignore

Create `.dockerignore`:

```
# Git
.git
.gitignore

# Documentation
*.md
LICENSE
docs/

# Development
.env
.env.*
*.log
__pycache__
*.pyc
.pytest_cache
.coverage
htmlcov/
dist/
build/
*.egg-info/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Config files (will be mounted)
litellm_config.yaml
config/
```

### docker-compose.yml

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  litellm:
    build:
      context: .
      dockerfile: Dockerfile
      args:
        - PYTHON_VERSION=3.11
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
      - /app/.cache
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:4000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## Running Your Custom Image

### Basic Run

```bash
docker run -d \
  --name litellm-proxy \
  -v $(pwd)/litellm_config.yaml:/app/config.yaml:ro \
  -p 4000:4000 \
  litellm-proxy:custom \
  --config /app/config.yaml
```

### Production Run

```bash
docker run -d \
  --name litellm-proxy \
  --restart always \
  --memory="512m" \
  --cpus="0.5" \
  --security-opt no-new-privileges:true \
  --read-only \
  --tmpfs /tmp:noexec,nosuid,size=100m \
  -v $(pwd)/litellm_config.yaml:/app/config.yaml:ro \
  -p 127.0.0.1:4000:4000 \
  litellm-proxy:custom \
  --config /app/config.yaml
```

### With Environment Variables Only

```bash
docker run -d \
  --name litellm-proxy \
  -e OPENWEBUI_API_KEY="your-api-key" \
  -e OPENWEBUI_API_BASE="http://myinstance.com/api" \
  -p 4000:4000 \
  litellm-proxy:custom \
  --model openai/openwebui-model \
  --api_base "$OPENWEBUI_API_BASE" \
  --api_key "$OPENWEBUI_API_KEY"
```

## Image Optimization

### Size Comparison

| Build Type | Base Image | Final Size | Build Time |
|------------|------------|------------|------------|
| Official | Full Python | 500-800MB | N/A |
| Slim | python:3.11-slim | 150-250MB | 2-3 min |
| Multi-stage | python:3.11-slim | 120-180MB | 3-4 min |
| Alpine | python:3.11-alpine | 80-120MB | 5-10 min |
| Security-hardened | python:3.11-slim | 150-200MB | 3-4 min |

### Further Optimization

1. **Remove Unnecessary Locales**:
```dockerfile
RUN apt-get update && apt-get install -y locales-all && \
    locale-gen en_US.UTF-8 && \
    apt-get purge -y locales-all && \
    apt-get clean
```

2. **Strip Python Packages**:
```dockerfile
RUN find /opt/venv -name "*.so" -exec strip {} \;
```

3. **Use Distroless Base** (experimental):
```dockerfile
FROM gcr.io/distroless/python3-debian11
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
```

## Testing Your Build

### Smoke Test

```bash
# Test the image
docker run --rm litellm-proxy:custom --version

# Test with config
docker run --rm \
  -v $(pwd)/litellm_config.yaml:/app/config.yaml:ro \
  litellm-proxy:custom \
  --config /app/config.yaml --check
```

### Security Scan

```bash
# Scan with Trivy
trivy image litellm-proxy:custom

# Scan with Docker Scout
docker scout cves litellm-proxy:custom
```

### Performance Test

```bash
# Benchmark startup time
time docker run --rm litellm-proxy:custom --help

# Check resource usage
docker stats --no-stream litellm-proxy
```

## CI/CD Integration

### GitHub Actions

Create `.github/workflows/docker-build.yml`:

```yaml
name: Build Custom Docker Image

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Build and test
      run: |
        docker build -t litellm-proxy:test .
        docker run --rm litellm-proxy:test --version
    
    - name: Security scan
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: litellm-proxy:test
        format: 'sarif'
        output: 'trivy-results.sarif'
```

## Troubleshooting

### Build Failures

```bash
# Build with no cache
docker build --no-cache -t litellm-proxy:custom .

# Verbose build
DOCKER_BUILDKIT=1 docker build --progress=plain -t litellm-proxy:custom .
```

### Runtime Issues

```bash
# Debug shell access
docker run -it --rm --entrypoint /bin/sh litellm-proxy:custom

# Check dependencies
docker run --rm litellm-proxy:custom pip list
```

## Best Practices

1. **Pin Versions**: Always pin Python and pip package versions
2. **Layer Caching**: Order Dockerfile commands from least to most frequently changing
3. **Security**: Run as non-root, use read-only filesystem
4. **Size**: Remove unnecessary files, use multi-stage builds
5. **Updates**: Regularly rebuild to get security patches