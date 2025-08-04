server {
    server_name brandonbryant.io;

    location / {
        return 200 "Welcome to brandonbryant.io - Access OpenWebUI at https://ai.brandonbryant.io";
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