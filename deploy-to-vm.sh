#!/bin/bash
# Lab 6 VM Deployment Script
# Run this script on your VM after SSH connection is available

set -e

VM_IP="10.93.26.121"
GITHUB_USER="vanya630"
REPO_URL="https://github.com/${GITHUB_USER}/se-toolkit-lab-6.git"
ENV_FILE=".env.docker.secret"

# Credentials (must match your local setup)
LMS_API_KEY="vanya630-lms-secret-key-2026"
AUTOCHECKER_EMAIL="i.grishaev@innopolis.university"
AUTOCHECKER_PASSWORD="vanya630yarunit"

echo "=== Lab 6 VM Deployment ==="
echo "Repository: ${REPO_URL}"
echo ""

# Step 1: Clone the repository
echo "[1/6] Cloning repository..."
cd ~
if [ -d "se-toolkit-lab-6" ]; then
    echo "  Repository exists, pulling latest changes..."
    cd se-toolkit-lab-6
    git pull
else
    echo "  Cloning repository..."
    git clone "${REPO_URL}"
    cd se-toolkit-lab-6
fi

# Step 2: Create environment file
echo "[2/6] Creating environment file..."
cp .env.docker.example .env.docker.secret

# Step 3: Configure credentials
echo "[3/6] Configuring credentials..."
sed -i "s/LMS_API_KEY=.*/LMS_API_KEY=${LMS_API_KEY}/" .env.docker.secret
sed -i "s/AUTOCHECKER_EMAIL=.*/AUTOCHECKER_EMAIL=${AUTOCHECKER_EMAIL}/" .env.docker.secret
sed -i "s/AUTOCHECKER_PASSWORD=.*/AUTOCHECKER_PASSWORD=${AUTOCHECKER_PASSWORD}/" .env.docker.secret

# Step 4: Start services
echo "[4/6] Starting Docker services..."
docker compose --env-file .env.docker.secret down || true
docker compose --env-file .env.docker.secret up --build -d

# Wait for services to be healthy
echo "  Waiting for services to start..."
sleep 10

# Step 5: Check services
echo "[5/6] Checking services..."
docker compose --env-file .env.docker.secret ps --format "table {{.Service}}\t{{.Status}}"

# Step 6: Populate database
echo "[6/6] Populating database..."
echo "  Running ETL sync..."
RESPONSE=$(curl -s -X POST "http://localhost:42002/pipeline/sync" \
    -H "Authorization: Bearer ${LMS_API_KEY}" \
    -H "Content-Type: application/json" \
    -d '{}')

echo "  ETL Response: ${RESPONSE}"

# Verify data
echo "  Verifying data..."
ITEMS_COUNT=$(curl -s "http://localhost:42002/items/" \
    -H "Authorization: Bearer ${LMS_API_KEY}" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")
echo "  Items loaded: ${ITEMS_COUNT}"

echo ""
echo "=== Deployment Complete ==="
echo "Backend API: http://${VM_IP}:42001"
echo "Frontend:    http://${VM_IP}:42002"
echo "pgAdmin:     http://${VM_IP}:42003"
echo "PostgreSQL:  ${VM_IP}:42004"
echo ""
echo "Next steps:"
echo "1. Set up Qwen Code API on the VM (see wiki/qwen.md)"
echo "2. Update .env.agent.secret with LLM_API_KEY and VM IP"
echo "3. Test the agent with: python agent.py"
