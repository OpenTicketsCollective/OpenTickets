#!/bin/sh

# Ensure certs directory exists with proper permissions
mkdir -p /etc/nginx/certs
chmod 755 /etc/nginx/certs

# Generate self-signed certificate if it doesn't exist
if [ ! -f /etc/nginx/certs/cert.pem ] || [ ! -f /etc/nginx/certs/key.pem ]; then
    echo "[*] Generating self-signed certificate..."
    openssl req -x509 -newkey rsa:4096 \
        -keyout /etc/nginx/certs/key.pem \
        -out /etc/nginx/certs/cert.pem \
        -days 365 -nodes \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
    
    if [ $? -eq 0 ]; then
        echo "[OK] Certificate generated successfully"
        ls -la /etc/nginx/certs/
    else
        echo "[ERROR] Certificate generation failed!"
        exit 1
    fi
else
    echo "[OK] Certificate already exists"
    ls -la /etc/nginx/certs/
fi

# Start nginx
echo "[*] Starting nginx..."
exec "$@"
