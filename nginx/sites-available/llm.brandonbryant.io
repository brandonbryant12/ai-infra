server {
    server_name llm.brandonbryant.io;

    # LiteLLM proxy
    location / {
        proxy_pass http://localhost:4000;
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

        # Pass through authorization headers
        proxy_set_header Authorization $http_authorization;
        proxy_pass_header Authorization;

        # Timeout settings
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # Buffer settings for streaming responses
        proxy_buffering off;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        proxy_busy_buffers_size 8k;
    }

    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/llm.brandonbryant.io/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/llm.brandonbryant.io/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot

}server {
    if ($host = llm.brandonbryant.io) {
        return 301 https://$host$request_uri;
    } # managed by Certbot


    listen 80;
    server_name llm.brandonbryant.io;
    return 404; # managed by Certbot


}