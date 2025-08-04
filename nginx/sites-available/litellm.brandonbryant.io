server {
    if ($host = litellm.brandonbryant.io) {
        return 301 https://$host$request_uri;
    } # managed by Certbot

    server_name litellm.brandonbryant.io;
    listen 80;
    return 404; # managed by Certbot
}

server {
    server_name litellm.brandonbryant.io;

    # Proxy all paths (API + UI) to the LiteLLM container listening on localhost:4000
    location / {
        proxy_pass http://localhost:4000;
        proxy_http_version 1.1;

        # WebSockets / Server-Sent Events
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Forwarded headers
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # Keep request/streaming stable
        proxy_buffering off;
        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;

        # Allow larger bodies for long prompts/tools
        client_max_body_size 50M;
    }

    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/litellm.brandonbryant.io/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/litellm.brandonbryant.io/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
}