#!/bin/bash
# Lab 6 - Complete VM Setup Script
# This script sets up:
# 1. autochecker user with SSH key access
# 2. Backend services (docker compose)
# 3. Qwen Code API
#
# Usage: Run this script on your VM after connecting via SSH
# Example: ssh root@10.93.25.246 "bash -s" < setup-vm-complete.sh

set -e

# === Configuration ===
GITHUB_USER="vanya630"
REPO_URL="https://github.com/${GITHUB_USER}/se-toolkit-lab-6.git"
LMS_API_KEY="vanya630-lms-secret-key-2026"
AUTOCHECKER_EMAIL="i.grishaev@innopolis.university"
AUTOCHECKER_PASSWORD="vanya630yarunit"
QWEN_API_KEY="your-qwen-api-key-here"  # You'll get this after Qwen auth
QWEN_API_PORT="8080"
VM_IP="10.93.26.121"

echo "=============================================="
echo "Lab 6 - Complete VM Setup"
echo "=============================================="
echo ""

# === Step 1: Create autochecker user ===
echo "[Step 1/6] Creating autochecker user..."
if id "autochecker" &>/dev/null; then
    echo "  User 'autochecker' already exists."
else
    useradd -m -s /bin/bash autochecker
    echo "  User 'autochecker' created."
fi

# Create .ssh directory for autochecker
mkdir -p /home/autochecker/.ssh
chmod 700 /home/autochecker/.ssh
chown autochecker:autochecker /home/autochecker/.ssh

# Add the official autochecker SSH public key
# From: wiki/vm-autochecker.md
AUTOCHKER_KEY="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKiL0DDQZw7L0Uf1c9cNlREY7IS6ZkIbGVWNsClqGNCZ se-toolkit-autochecker"
echo "${AUTOCHKER_KEY}" > /home/autochecker/.ssh/authorized_keys
chmod 600 /home/autochecker/.ssh/authorized_keys
chown autochecker:autochecker /home/autochecker/.ssh/authorized_keys

echo "  SSH key configured for autochecker user."
echo ""

# === Step 2: Clone the repository ===
echo "[Step 2/6] Cloning repository..."
cd ~
if [ -d "se-toolkit-lab-6" ]; then
    echo "  Repository exists, pulling latest..."
    cd se-toolkit-lab-6
    git pull
else
    echo "  Cloning repository..."
    git clone "${REPO_URL}"
    cd se-toolkit-lab-6
fi

# === Step 3: Create and configure environment file ===
echo "[Step 3/6] Configuring environment..."
cp .env.docker.example .env.docker.secret

# Update credentials
sed -i "s/^LMS_API_KEY=.*/LMS_API_KEY=${LMS_API_KEY}/" .env.docker.secret
sed -i "s/^AUTOCHECKER_EMAIL=.*/AUTOCHECKER_EMAIL=${AUTOCHECKER_EMAIL}/" .env.docker.secret
sed -i "s/^AUTOCHECKER_PASSWORD=.*/AUTOCHECKER_PASSWORD=${AUTOCHECKER_PASSWORD}/" .env.docker.secret

# Fix Docker images to use Docker Hub (avoid Harbor timeout issues)
echo "  Updating Dockerfiles to use Docker Hub images..."

# Update backend Dockerfile
sed -i 's|FROM harbor\.pg\.innopolis\.university/docker-hub-cache/astral/uv:python3\.14-bookworm-slim|FROM astral/uv:python3.14-bookworm-slim|' Dockerfile
sed -i 's|FROM harbor\.pg\.innopolis\.university/docker-hub-cache/python:3\.14\.2-slim-bookworm|FROM python:3.14.2-slim-bookworm|' Dockerfile

# Update frontend Dockerfile
sed -i 's|FROM harbor\.pg\.innopolis\.university/docker-hub-cache/node:25-alpine|FROM node:25-alpine|' frontend/Dockerfile
sed -i 's|FROM harbor\.pg\.innopolis\.university/docker-hub-cache/caddy:2\.11-alpine|FROM caddy:2.11-alpine|' frontend/Dockerfile

# Update docker-compose.yml
sed -i 's|image: harbor\.pg\.innopolis\.university/docker-hub-cache/postgres:18\.3-alpine|image: postgres:18.3-alpine|' docker-compose.yml
sed -i 's|image: harbor\.pg\.innopolis\.university/docker-hub-cache/dpage/pgadmin4:latest|image: dpage/pgadmin4:latest|' docker-compose.yml

echo "  Environment configured."
echo ""

# === Step 4: Start Docker services ===
echo "[Step 4/6] Starting Docker services..."
docker compose --env-file .env.docker.secret down || true
docker compose --env-file .env.docker.secret up --build -d

echo "  Waiting for services to start..."
sleep 15

# Check services
echo "  Checking services..."
docker compose --env-file .env.docker.secret ps --format "table {{.Service}}\t{{.Status}}"
echo ""

# === Step 5: Populate database ===
echo "[Step 5/6] Populating database..."
echo "  Running ETL sync..."
RESPONSE=$(curl -s -X POST "http://localhost:42002/pipeline/sync" \
    -H "Authorization: Bearer ${LMS_API_KEY}" \
    -H "Content-Type: application/json" \
    -d '{}')

echo "  ETL Response: ${RESPONSE}"

# Verify
ITEMS_COUNT=$(curl -s "http://localhost:42002/items/" \
    -H "Authorization: Bearer ${LMS_API_KEY}" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
echo "  Items loaded: ${ITEMS_COUNT}"

if [ "${ITEMS_COUNT}" -gt 0 ]; then
    echo "  ✅ Database populated successfully."
else
    echo "  ⚠️ Warning: No items loaded. Check autochecker credentials."
fi
echo ""

# === Step 6: Set up Qwen Code API ===
echo "[Step 6/6] Setting up Qwen Code API..."

# Install pnpm if not installed
if ! command -v pnpm &> /dev/null; then
    echo "  Installing pnpm..."
    npm install -g pnpm
fi

# Install Qwen Code CLI
if ! command -v qwen &> /dev/null; then
    echo "  Installing Qwen Code CLI..."
    pnpm add -g @qwen-code/qwen-code
fi

echo ""
echo "  ⚠️  IMPORTANT: You need to authenticate Qwen Code manually."
echo "  Run these commands:"
echo "    qwen"
echo "    /auth"
echo "  Then open the link in your browser and complete authentication."
echo "  After that, note your QWEN_API_KEY from ~/.qwen/oauth_creds.json"
echo ""

# Clone Qwen API proxy
if [ ! -d "~/qwen-code-oai-proxy" ]; then
    echo "  Cloning qwen-code-oai-proxy..."
    git clone https://github.com/inno-se-toolkit/qwen-code-oai-proxy ~/qwen-code-oai-proxy
fi

cd ~/qwen-code-oai-proxy
cp .env.example .env

# Update .env with port
sed -i "s/^HOST_PORT=.*/HOST_PORT=${QWEN_API_PORT}/" .env

echo ""
echo "  ⚠️  IMPORTANT: Update ~/qwen-code-oai-proxy/.env with your QWEN_API_KEY"
echo "  After authenticating with Qwen, run:"
echo "    cat ~/.qwen/oauth_creds.json | jq -r '.api_key'"
echo "  Then edit .env and set QWEN_API_KEY to that value."
echo ""

echo "=============================================="
echo "Setup Complete!"
echo "=============================================="
echo ""
echo "Next steps:"
echo "1. Authenticate Qwen Code: qwen -> /auth"
echo "2. Get your API key: cat ~/.qwen/oauth_creds.json | jq -r '.api_key'"
echo "3. Update ~/qwen-code-oai-proxy/.env with QWEN_API_KEY"
echo "4. Start Qwen API: cd ~/qwen-code-oai-proxy && docker compose up --build -d"
echo "5. Test: curl http://localhost:${QWEN_API_PORT}/v1/chat/completions -H 'Authorization: Bearer <key>' -H 'Content-Type: application/json' -d '{\"model\":\"qwen3-coder-plus\",\"messages\":[{\"role\":\"user\",\"content\":\"Hi\"}]}'"
echo ""
echo "Service URLs:"
echo "  Backend API:  http://${VM_IP}:42001"
echo "  Frontend:     http://${VM_IP}:42002"
echo "  pgAdmin:      http://${VM_IP}:42003"
echo "  PostgreSQL:   ${VM_IP}:42004"
echo "  Qwen API:     http://${VM_IP}:${QWEN_API_PORT}/v1"
echo ""
echo "To verify autochecker SSH access:"
echo "  ssh -i /path/to/autochecker_key autochecker@${VM_IP} 'echo SSH works'"
