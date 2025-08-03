# Nginx Configuration

This directory contains the nginx server configurations for the AI infrastructure services.

## Server Blocks

### brandonbryant.io
- **File**: `sites-available/brandonbryant.io`
- **Purpose**: Main domain with OpenWebUI proxied at `/ai/` path
- **Features**:
  - SSL/TLS termination with Let's Encrypt certificates
  - WebSocket support for real-time features
  - Static asset proxying for optimal performance
  - Proper headers for reverse proxy operation

### ai.brandonbryant.io  
- **File**: `sites-available/ai.brandonbryant.io`
- **Purpose**: Dedicated subdomain for OpenWebUI (alternative access method)
- **Features**:
  - Direct proxy to OpenWebUI container
  - SSL/TLS termination
  - WebSocket support

## Key Configuration Details

### OpenWebUI Proxy Configuration
```nginx
location /ai/ {
    proxy_pass http://localhost:3000/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Prefix /ai;
    proxy_cache_bypass $http_upgrade;
}
```

### Important Notes
- The proxy strips the `/ai` path when forwarding to OpenWebUI
- OpenWebUI runs on port 3000 locally
- WebSocket support is enabled for real-time features
- Static assets are proxied separately for better caching

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
- **502 Bad Gateway**: Check if OpenWebUI container is running on port 3000
- **WebSocket connection failed**: Verify WebSocket headers and upgrade handling
- **Static assets not loading**: Check static asset proxy configuration

### Useful Commands
```bash
# Check nginx error logs
sudo tail -f /var/log/nginx/error.log

# Test configuration
sudo nginx -t

# Reload configuration
sudo systemctl reload nginx
```