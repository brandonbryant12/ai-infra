server {
    server_name brandonbryant.io;

    # OpenWebUI at /ai path - with proper API routing
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
        
        # WebSocket support
        proxy_set_header Sec-WebSocket-Extensions $http_sec_websocket_extensions;
        proxy_set_header Sec-WebSocket-Key $http_sec_websocket_key;
        proxy_set_header Sec-WebSocket-Version $http_sec_websocket_version;
        
        # Timeout settings
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Handle /ai without trailing slash
    location = /ai {
        return 301 /ai/;
    }
    
    # Proxy static assets that OpenWebUI requests at root level
    location /static/ {
        proxy_pass http://localhost:3000/static/;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        add_header Cache-Control "public, max-age=31536000";
    }
    
    # Proxy app assets
    location /_app/ {
        proxy_pass http://localhost:3000/_app/;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        add_header Cache-Control "public, max-age=31536000";
    }
    
    # Proxy manifest and other root assets
    location ~ ^/(manifest\.json|opensearch\.xml|favicon\.(ico|png)|apple-touch-icon\.png)$ {
        proxy_pass http://localhost:3000$uri;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        add_header Cache-Control "public, max-age=31536000";
    }

    # Root location - serve a landing page (must be last)
    location / {
        return 200 "Welcome to brandonbryant.io - Access OpenWebUI at /ai";
        add_header Content-Type text/plain;
    }

    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/brandonbryant.io/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/brandonbryant.io/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot

}

server {
    if ($host = brandonbryant.io) {
        return 301 https://$host$request_uri;
    } # managed by Certbot

    listen 80;
    server_name brandonbryant.io;
    return 404; # managed by Certbot
}