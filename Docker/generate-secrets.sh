#!/bin/bash

# Generate .env with high-entropy random passwords if it doesn't exist
if [ ! -f .env ]; then
    echo "[*] Generating .env with high-entropy passwords (512-bit)..."
    
    ROOT_PASS=$(openssl rand -hex 64)
    APP_PASS=$(openssl rand -hex 64)
    
    cat > .env <<EOF
MYSQL_ROOT_PASSWORD=$ROOT_PASS
MYSQL_APP_USER=opentickets_app
MYSQL_APP_PASSWORD=$APP_PASS
EOF
    
    echo "[OK] .env created with random passwords"
else
    echo "[OK] .env already exists, skipping generation"
fi
