# Nginx Configuration

This directory contains the nginx server configurations for the AI infrastructure services.

## Server Blocks

### brandonbryant.io
- **File**: `sites-available/brandonbryant.io`
- **Purpose**: Main domain landing page only; **no** reverse proxy for OpenWebUI
- **Features**:
  - SSL/TLS termination with Let's Encrypt certificates
  - Simple landing that points users to the AI subdomain

### ai.brandonbryant.io  
- **File**: `sites-available/ai.brandonbryant.io`
- **Purpose**: Dedicated subdomain for OpenWebUI
- **Features**:
  - Direct proxy to OpenWebUI container
  - SSL/TLS termination
  - WebSocket support
  - Proper forwarded headers for reverse proxy operation

### litellm.brandonbryant.io
- **File**: `sites-available/litellm.brandonbryant.io`
- **Purpose**: LiteLLM Gateway (API + Admin UI)
- **Features**:
  - Proxy to LiteLLM API endpoints and web interface
  - SSL/TLS termination
  - Static asset caching for UI
  - Session cookie handling
  - UI authentication support
  - WebSocket support for streaming API responses
- **LiteLLM Gateway**: OpenAI-compatible API gateway with dynamic OpenRouter integration (295+ models) and **Langfuse tracing** built-in
- **Observability (Langfuse)**: Full traces, usage & cost analytics, evaluations

## Key Configuration Details

### OpenWebUI Proxy Configuration (subdomain)
```nginx
server {
    server_name ai.brandonbryant.io;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_redirect off;
    }
}
````

### Important Notes

* OpenWebUI is served on the **subdomain** `ai.brandonbryant.io`
* OpenWebUI runs on port 3000 locally (proxied by nginx)
* LiteLLM Gateway (API + UI) is served on `litellm.brandonbryant.io`
* LiteLLM runs on port 4000 locally (proxied by nginx)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/brandonbryant12/ai-infra.git
cd ai-infra

# Run setup script (first time only)
./scripts/setup.sh

# Edit environment files
vim stacks/openwebui/.env    # Set WEBUI_SECRET_KEY, WEBUI_URL, ENABLE_FORWARD_USER_INFO_HEADERS=true (default already)
vim stacks/langfuse/.env     # Set POSTGRES_PASSWORD, NEXTAUTH_SECRET, LANGFUSE_SALT, LANGFUSE_URL; (optional) LANGFUSE_INIT_* to auto-provision keys
vim stacks/litellm/.env      # Set OPENROUTER_API_KEY; after Langfuse boots, set LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST

# Start all services
make start

# Check status
make status
```

## LiteLLM Gateway Services (litellm.brandonbryant.io)

### API Endpoint
- **URL**: `https://litellm.brandonbryant.io/v1`
- **Authentication**: API Key (Bearer token)
- **Use Case**: OpenAI-compatible API for model access

### Admin UI
- **URL**: `https://litellm.brandonbryant.io/ui`
- **Authentication**: Username/Password (configured in .env)
- **Features**:
  - API key management
  - Model configuration
  - Usage tracking and spend monitoring
  - User management (requires database configuration)
* WebSocket support is enabled for real-time features

### User Header Flow

* OpenWebUI forwards user info as `X-OpenWebUI-User-*` headers
* LiteLLM Gateway uses your configured `X-OpenWebUI-User-Id` for user attribution (set in `config.yaml.j2`)
* All services share the `llmnet` Docker network for communication

### Endpoints

* **OpenWebUI**: `https://ai.brandonbryant.io`
* **LiteLLM API & UI**: `https://litellm.brandonbryant.io`
* **Langfuse UI**: `https://langfuse.brandonbryant.io`

## Installation

1. Copy configurations to nginx sites-available:

   ```bash
   sudo cp sites-available/* /etc/nginx/sites-available/
   ```

2. Enable the sites:

   ```bash
   sudo ln -s /etc/nginx/sites-available/brandonbryant.io /etc/nginx/sites-enabled/
   sudo ln -s /etc/nginx/sites-available/ai.brandonbryant.io /etc/nginx/sites-enabled/
   ```

3. Test configuration:

   ```bash
   sudo nginx -t
   ```

4. Reload nginx:

   ```bash
   sudo systemctl reload nginx
   ```

## SSL Certificates

The configurations reference Let's Encrypt certificates. Ensure certificates are obtained using:

```bash
sudo certbot --nginx -d brandonbryant.io -d ai.brandonbryant.io
```

## Troubleshooting

### Common Issues

* **502 Bad Gateway**: Check if OpenWebUI container is running on port 3000
* **WebSocket connection failed**: Verify WebSocket headers and upgrade handling
* **Static assets not loading**: Confirm the subdomain proxy block

### Useful Commands

```bash
# Check nginx error logs
sudo tail -f /var/log/nginx/error.log

# Test configuration
sudo nginx -t

# Reload configuration
sudo systemctl reload nginx
```

### Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌─────────────┐
│   Users     │────▶│   OpenWebUI  │────▶│ LiteLLM     │────▶│ OpenRouter  │
│             │     │   (Port 3000)│     │ (Port 4000) │     │  API        │
└─────────────┘     └──────────────┘     └─────────────┘     └─────────────┘
                           │
                           └──────────────▶ Langfuse (Traces, Port 3100)
```

### Automatic Updates

```bash
make update   # Pull latest & restart OpenWebUI, LiteLLM, and Langfuse
```
\