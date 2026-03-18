# 🚀 Lab 6 VM Deployment - Quick Start

## New VM IP: `10.93.26.121`

---

## ⚡ One-Command Deployment

**From university network or VPN, run:**

```bash
cd /Users/ivangrishaev/software-engineering-toolkit/se-toolkit-lab-6 && \
scp setup-vm-complete.sh root@10.93.26.121:~/ && \
ssh root@10.93.26.121 "bash -s" < setup-vm-complete.sh
```

---

## ✅ What This Does

1. Creates `autochecker` user with SSH key
2. Clones your GitHub repo (`vanya630/se-toolkit-lab-6`)
3. Configures Docker environment
4. Starts all 4 services (app, caddy, postgres, pgadmin)
5. Populates database via ETL pipeline
6. Prepares Qwen Code API setup

---

## 🔐 After Deployment: Qwen Authentication

```bash
# SSH into VM
ssh root@10.93.26.121

# Authenticate Qwen
qwen
# Type: /auth
# Open the link in browser and authenticate
# Copy your API key

# Exit qwen
/quit
```

---

## 🔧 Configure Qwen API

```bash
# Edit Qwen proxy config
cd ~/qwen-code-oai-proxy
nano .env

# Set your API key (paste the key you copied):
# QWEN_API_KEY=your-actual-key-here

# Save: Ctrl+O, Enter, Ctrl+X

# Start Qwen API
docker compose up --build -d

# Test
curl -s http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $(grep QWEN_API_KEY .env | cut -d'=' -f2)" \
  -d '{"model":"qwen3-coder-plus","messages":[{"role":"user","content":"Hi"}]}'
```

---

## ✅ Verify Deployment

```bash
# Test 1: Autochecker SSH
ssh -o StrictHostKeyChecking=no autochecker@10.93.26.121 "echo 'SSH OK'"

# Test 2: Backend API
curl -s http://10.93.26.121:42002/items/ \
  -H "Authorization: Bearer vanya630-lms-secret-key-2026" | head -c 100

# Test 3: Services running
docker compose --env-file .env.docker.secret ps
```

---

## 🌐 Service URLs

| Service | URL |
|---------|-----|
| Frontend | http://10.93.26.121:42002 |
| Swagger | http://10.93.26.121:42002/docs |
| pgAdmin | http://10.93.26.121:42003 |
| Qwen API | http://10.93.26.121:8080/v1 |

---

## 🔑 Your Credentials

```
LMS_API_KEY=vanya630-lms-secret-key-2026
AUTOCHECKER_EMAIL=i.grishaev@innopolis.university
AUTOCHECKER_PASSWORD=vanya630yarunit
```

---

## 📁 Files Ready

| File | Status |
|------|--------|
| `setup-vm-complete.sh` | ✅ Ready to deploy |
| `.env.docker.secret` | ✅ Configured |
| `.env.agent.secret` | ✅ VM IP updated |
| `VM_SETUP_GUIDE.md` | ✅ Full guide |

---

## ⚠️ Important

- **Network**: Must be on university network or VPN
- **Qwen API**: Requires manual authentication (1-time setup)
- **Keep VM running**: Autochecker needs 24/7 access

---

## 🆘 Troubleshooting

**"Connection timed out"**
→ Connect to university Wi-Fi or VPN first

**"Permission denied"**
→ Re-run: `ssh root@10.93.26.121 "bash -s" < setup-vm-complete.sh`

**"Port already allocated"**
→ Run: `docker compose --env-file .env.docker.secret down && docker compose --env-file .env.docker.secret up --build -d`

---

**Next**: After deployment, proceed to Task 1 (Call an LLM from code)
