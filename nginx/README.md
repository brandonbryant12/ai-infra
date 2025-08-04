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

### llm.brandonbryant.io
- **File**: `sites-available/llm.brandonbryant.io`
- **Purpose**: LiteLLM API Gateway endpoint
- **Features**:
  - Proxy to LiteLLM container API endpoints
  - SSL/TLS termination
  - WebSocket support for streaming responses
  - Authorization header passthrough
  - Optimized for API traffic with disabled buffering

### litellm.brandonbryant.io
- **File**: `sites-available/litellm.brandonbryant.io`
- **Purpose**: LiteLLM Admin UI
- **Features**:
  - Proxy to LiteLLM web interface
  - SSL/TLS termination
  - Static asset caching
  - Session cookie handling
  - UI authentication support

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
* LiteLLM API Gateway is served on `llm.brandonbryant.io`
* LiteLLM Admin UI is served on `litellm.brandonbryant.io`
* LiteLLM runs on port 4000 locally (proxied by nginx)

## LiteLLM Services

### API Gateway (llm.brandonbryant.io)
- **Endpoint**: `https://llm.brandonbryant.io/v1`
- **Authentication**: API Key (Bearer token)
- **Use Case**: OpenAI-compatible API for model access

### Admin UI (litellm.brandonbryant.io)
- **URL**: `https://litellm.brandonbryant.io/ui`
- **Authentication**: Username/Password (configured in .env)
- **Features**:
  - API key management
  - Model configuration
  - Usage tracking and spend monitoring
  - User management
* WebSocket support is enabled for real-time features

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

\