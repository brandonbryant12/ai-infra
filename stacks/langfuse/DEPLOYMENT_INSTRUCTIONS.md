# Langfuse Deployment Instructions for 129.212.197.76

## Files to Transfer
1. `docker-compose.yml` - Main Langfuse configuration
2. `.env` - Environment variables with secrets
3. `langfuse-nginx.conf` - Nginx configuration

## Deployment Steps on 129.212.197.76

### 1. Setup Directory
```bash
mkdir -p /root/ai-infra/stacks/langfuse
cd /root/ai-infra/stacks/langfuse
```

### 2. Transfer Files
Copy the three files above to the langfuse directory

### 3. Deploy Langfuse
```bash
# Start Langfuse services
docker compose up -d

# Wait for containers to be healthy (2-3 minutes)
docker ps | grep langfuse
```

### 4. Configure Nginx
```bash
# Copy nginx config
cp langfuse-nginx.conf /etc/nginx/sites-available/langfuse.brandonbryant.io

# Enable site
ln -s /etc/nginx/sites-available/langfuse.brandonbryant.io /etc/nginx/sites-enabled/

# Test configuration
nginx -t

# Reload nginx
systemctl reload nginx
```

### 5. SSL Certificate
If SSL certificate doesn't exist for langfuse.brandonbryant.io:
```bash
certbot --nginx -d langfuse.brandonbryant.io
```

### 6. Verify Deployment
- Check containers: `docker ps | grep langfuse`
- Test locally: `curl -I http://localhost:3100/`
- Test domain: `curl -I https://langfuse.brandonbryant.io/`

## Important Notes
- Port 3100 must be available
- Ensure llmnet Docker network exists: `docker network create llmnet`
- First user to register becomes admin
- All secrets are already configured in .env file

## Troubleshooting
- Check logs: `docker logs langfuse-langfuse-web-1`
- Check nginx: `systemctl status nginx`
- Check DNS: `nslookup langfuse.brandonbryant.io`