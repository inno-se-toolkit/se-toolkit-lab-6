# Lab 6 VM Setup Guide

## Problem

The autochecker reports two failures:
1. ❌ SSH login as autochecker works - Permission denied
2. ❌ Backend is running on VM (port 42002) - Connection failed

## Solution

You need to connect to your VM (from university network or VPN) and run the setup script.

**New VM IP: `10.93.26.121`**

---

## Step-by-Step Instructions

### Step 1: Connect to University Network

The VM (10.93.25.246) is only accessible from the university network. You have two options:

**Option A: Connect from University Campus**
- Connect to the university Wi-Fi or wired network
- Open Terminal/VS Code

**Option B: Use University VPN**
- Connect to the university VPN first
- Then proceed with the steps below

### Step 2: Test SSH Connection

Open Terminal and test the connection:

```bash
ssh root@10.93.26.121
```

If this works, you're ready to deploy.

### Step 3: Run the Complete Setup Script

The script will:
1. Create the `autochecker` user with SSH key access
2. Clone your repository
3. Configure Docker environment
4. Start all services (app, caddy, postgres, pgadmin)
5. Populate the database via ETL
6. Set up Qwen Code API (requires manual auth)

**Run these commands on your local machine:**

```bash
# Navigate to the lab directory
cd /Users/ivangrishaev/software-engineering-toolkit/se-toolkit-lab-6

# Copy the setup script to your VM
scp setup-vm-complete.sh root@10.93.26.121:~/

# SSH into your VM and run the script
ssh root@10.93.26.121 "bash -s" < setup-vm-complete.sh
```

### Step 4: Authenticate Qwen Code (Manual Step)

After the script completes, you need to authenticate Qwen Code:

```bash
# SSH into your VM
ssh root@10.93.26.121

# Run Qwen and authenticate
qwen
# In the chat, type: /auth
# Open the link in your browser and complete authentication

# Get your API key
exit  # Exit qwen chat
cat ~/.qwen/oauth_creds.json | jq -r '.api_key'
```

Copy the API key output.

### Step 5: Configure Qwen API Proxy

```bash
# SSH into your VM (if not already connected)
ssh root@10.93.26.121

# Navigate to the Qwen proxy directory
cd ~/qwen-code-oai-proxy

# Edit the .env file
nano .env

# Set your QWEN_API_KEY (paste the key you copied)
# Example:
# QWEN_API_KEY=your-actual-api-key-here
# HOST_PORT=8080

# Save: Ctrl+O, Enter, Ctrl+X

# Start the Qwen API service
docker compose up --build -d

# Test the API
curl -s http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $(cat .env | grep QWEN_API_KEY | cut -d'=' -f2)" \
  -d '{"model":"qwen3-coder-plus","messages":[{"role":"user","content":"What is 2+2?"}]}'
```

You should get a response like:
```json
{"choices":[{"message":{"content":"2 + 2 = 4."}}]}
```

### Step 6: Update Local .env.agent.secret

Back on your **local machine**, update the agent configuration:

```bash
cd /Users/ivangrishaev/software-engineering-toolkit/se-toolkit-lab-6
nano .env.agent.secret
```

Set these values:
```bash
LLM_API_KEY=<your-qwen-api-key-from-step-4>
LLM_API_BASE=http://10.93.26.121:8080/v1
LLM_MODEL=qwen3-coder-plus
```

### Step 7: Verify Everything Works

**Test 1: Autochecker SSH Access**
```bash
# The autochecker should now be able to connect
# (This is what the autochecker bot does)
ssh -o StrictHostKeyChecking=no autochecker@10.93.26.121 "echo 'SSH works!'"
```
Expected: `SSH works!`

**Test 2: Backend API**
```bash
curl -s http://10.93.26.121:42002/items/ \
  -H "Authorization: Bearer vanya630-lms-secret-key-2026" | head -c 200
```
Expected: JSON array of items

**Test 3: Qwen API from Local Machine**
```bash
curl -s http://10.93.26.121:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-qwen-api-key>" \
  -d '{"model":"qwen3-coder-plus","messages":[{"role":"user","content":"Hello!"}]}'
```
Expected: JSON response with assistant message

---

## Troubleshooting

### "Connection timed out"
- You're not on the university network
- Connect to university Wi-Fi or VPN first

### "Permission denied (publickey)"
- The autochecker user wasn't created properly
- Re-run the setup script

### "Port already allocated"
- Another service is using ports 42001, 42002, 42003, or 42004
- Run: `docker compose --env-file .env.docker.secret down`
- Then: `docker compose --env-file .env.docker.secret up --build -d`

### ETL returns 0 items
- Check your autochecker credentials in `.env.docker.secret`
- Verify: `AUTOCHECKER_EMAIL=i.grishaev@innopolis.university`
- Verify: `AUTOCHECKER_PASSWORD=vanya630yarunit`

---

## Files Created

| File | Purpose |
|------|---------|
| `setup-vm-complete.sh` | Complete VM setup script |
| `.env.docker.secret` | Docker environment (on VM) |
| `.env.agent.secret` | Agent LLM configuration (local) |
| `~/qwen-code-oai-proxy/.env` | Qwen API config (on VM) |

---

## Service URLs (after deployment)

| Service | URL |
|---------|-----|
| Backend API | http://10.93.26.121:42001 |
| Frontend | http://10.93.26.121:42002 |
| Swagger Docs | http://10.93.26.121:42002/docs |
| pgAdmin | http://10.93.26.121:42003 |
| Qwen API | http://10.93.26.121:8080/v1 |

---

## Your Credentials

| Setting | Value |
|---------|-------|
| LMS_API_KEY | `vanya630-lms-secret-key-2026` |
| AUTOCHECKER_EMAIL | `i.grishaev@innopolis.university` |
| AUTOCHECKER_PASSWORD | `vanya630yarunit` |
| GitHub | `vanya630` |
| VM IP | `10.93.26.121` |
| Qwen API Port | `8080` |

---

## Next Steps

After completing the setup:
1. ✅ Autochecker can SSH into your VM
2. ✅ Backend is running on port 42002
3. ✅ Qwen API is accessible
4. ⏭️ Proceed to Task 1: Call an LLM from code

See: [lab/tasks/required/task-1.md](lab/tasks/required/task-1.md)
