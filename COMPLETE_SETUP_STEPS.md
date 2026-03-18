# Lab 6 - Complete Setup Guide (Step by Step)

**Your VM IP:** `10.93.26.121`

---

## 📋 Overview

You need to complete these steps:

| Step | What | Where | Time |
|------|------|-------|------|
| 1 | Connect to university network | Your laptop | 1 min |
| 2 | Deploy backend to VM | Your laptop → VM | 5 min |
| 3 | Authenticate Qwen Code | VM | 2 min |
| 4 | Configure Qwen API | VM | 2 min |
| 5 | Update local config | Your laptop | 1 min |
| 6 | Verify everything works | Your laptop | 2 min |

**Total time:** ~15 minutes

---

## Step 1: Connect to University Network

The VM is only accessible from the university network.

**Option A: On Campus**
- Connect to university Wi-Fi

**Option B: Off Campus**
- Connect to university VPN first

Then open **VS Code Terminal** and continue.

---

## Step 2: Deploy Backend to VM

Run these commands in your **local VS Code Terminal**:

```bash
# 1. Navigate to lab directory
cd /Users/ivangrishaev/software-engineering-toolkit/se-toolkit-lab-6
```

```bash
# 2. Copy the setup script to your VM
scp setup-vm-complete.sh root@10.93.26.121:~/
```

```bash
# 3. Run the setup script on your VM
# This will take 3-5 minutes
ssh root@10.93.26.121 "bash -s" < setup-vm-complete.sh
```

**What happens:**
- Creates `autochecker` user with SSH key ✅
- Clones your GitHub repo ✅
- Configures Docker environment ✅
- Builds and starts 4 containers (app, caddy, postgres, pgadmin) ✅
- Populates database from autochecker API ✅

**Wait for:** `Setup Complete!` message

**Then:** Keep the SSH session open - you'll need it for Step 3.

---

## Step 3: Authenticate Qwen Code

**Stay connected to your VM** (or reconnect):

```bash
ssh root@10.93.26.121
```

Now authenticate Qwen Code:

```bash
# 1. Start Qwen Code CLI
qwen
```

```bash
# 2. In the Qwen chat, type:
/auth
```

**Qwen will show a URL** like:
```
https://oauth.qwen.ai/activate?code=XXXX
```

**Do this:**
1. Copy the URL
2. Open it in your browser
3. Log in with your Qwen account (or create one)
4. Complete authentication
5. Return to terminal

```bash
# 3. Exit Qwen chat
/quit
```

```bash
# 4. Get your API key
cat ~/.qwen/oauth_creds.json | jq -r '.api_key'
```

**Copy the output** - it looks like:
```
sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

You'll need this in Step 4.

---

## Step 4: Configure Qwen API Proxy

**Still on your VM:**

```bash
# 1. Go to Qwen proxy directory
cd ~/qwen-code-oai-proxy
```

```bash
# 2. Open the .env file
nano .env
```

**Find this line:**
```
QWEN_API_KEY=your-qwen-api-key-here
```

**Replace with your actual key:**
```
QWEN_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Save:**
- Press `Ctrl + O`
- Press `Enter`
- Press `Ctrl + X`

```bash
# 3. Start the Qwen API service
docker compose up --build -d
```

```bash
# 4. Wait for it to start
sleep 5
```

```bash
# 5. Test the Qwen API
curl -s http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $(grep QWEN_API_KEY .env | cut -d'=' -f2)" \
  -d '{"model":"qwen3-coder-plus","messages":[{"role":"user","content":"What is 2+2?"}]}'
```

**Expected response:**
```json
{"choices":[{"message":{"content":"2 + 2 = 4."}}]}
```

✅ **Qwen API is working!**

---

## Step 5: Update Local Configuration

**Back on your local laptop:**

```bash
# 1. Open the agent config file
cd /Users/ivangrishaev/software-engineering-toolkit/se-toolkit-lab-6
nano .env.agent.secret
```

**Update these lines:**

```bash
# Replace with your actual Qwen API key
LLM_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# VM IP (already correct)
LLM_API_BASE=http://10.93.26.121:8080/v1

# Model name (already correct)
LLM_MODEL=qwen3-coder-plus
```

**Save:**
- Press `Ctrl + O`
- Press `Enter`
- Press `Ctrl + X`

---

## Step 6: Verify Everything Works

### Test 1: Autochecker SSH Access

```bash
ssh -o StrictHostKeyChecking=no autochecker@10.93.26.121 "echo 'SSH works!'"
```

**Expected:** `SSH works!`

❌ **If fails:** Re-run Step 2 (the setup script creates the autochecker user)

---

### Test 2: Backend API

```bash
curl -s "http://10.93.26.121:42002/items/" \
  -H "Authorization: Bearer vanya630-lms-secret-key-2026" | head -c 200
```

**Expected:** JSON array starting with `[{"id":1,"title":"Lab...`

❌ **If fails:** SSH to VM and run:
```bash
ssh root@10.93.26.121
docker compose --env-file .env.docker.secret ps
```

---

### Test 3: Qwen API from Local Machine

```bash
# Get your API key from .env.agent.secret
cat .env.agent.secret | grep LLM_API_KEY
```

```bash
# Test the API (replace YOUR_KEY with actual key)
curl -s http://10.93.26.121:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_KEY" \
  -d '{"model":"qwen3-coder-plus","messages":[{"role":"user","content":"Hello!"}]}'
```

**Expected:** JSON response with assistant message

❌ **If fails:** Check Qwen API is running on VM:
```bash
ssh root@10.93.26.121
docker compose -f ~/qwen-code-oai-proxy/docker-compose.yml ps
```

---

### Test 4: Frontend (Optional)

Open in browser: **http://10.93.26.121:42002**

Enter API key: `vanya630-lms-secret-key-2026`

You should see the dashboard with charts.

---

## ✅ Setup Complete!

You should now have:

- ✅ Autochecker can SSH into your VM
- ✅ Backend running on port 42002
- ✅ Database populated with autochecker data
- ✅ Qwen API accessible at http://10.93.26.121:8080/v1
- ✅ Local agent configured

---

## 🎯 Next Steps

Proceed to the lab tasks:

1. **Task 1:** [Call an LLM from code](lab/tasks/required/task-1.md)
2. **Task 2:** [The documentation agent](lab/tasks/required/task-2.md)
3. **Task 3:** [The system agent](lab/tasks/required/task-3.md)

---

## 🆘 Troubleshooting

### "Connection timed out" (all steps)
**Problem:** Not on university network

**Fix:** Connect to university Wi-Fi or VPN, then retry

---

### "Permission denied (publickey)" for autochecker
**Problem:** Autochecker user not created properly

**Fix:** Re-run the setup script:
```bash
ssh root@10.93.26.121 "bash -s" < setup-vm-complete.sh
```

---

### "Port is already allocated"
**Problem:** Another container using the port

**Fix on VM:**
```bash
ssh root@10.93.26.121
docker compose --env-file .env.docker.secret down
docker compose --env-file .env.docker.secret up --build -d
```

---

### ETL returns 0 items
**Problem:** Wrong autochecker credentials

**Fix on VM:**
```bash
ssh root@10.93.26.121
cd ~/se-toolkit-lab-6
nano .env.docker.secret
```

Verify:
```
AUTOCHECKER_EMAIL=i.grishaev@innopolis.university
AUTOCHECKER_PASSWORD=vanya630yarunit
```

Then re-run ETL:
```bash
docker compose --env-file .env.docker.secret restart app
curl -X POST http://localhost:42002/pipeline/sync \
  -H "Authorization: Bearer vanya630-lms-secret-key-2026" \
  -H "Content-Type: application/json" -d '{}'
```

---

### Qwen API returns 401 Unauthorized
**Problem:** Wrong API key

**Fix:**
1. Get your key: `cat ~/.qwen/oauth_creds.json | jq -r '.api_key'`
2. Update on VM: `nano ~/qwen-code-oai-proxy/.env`
3. Restart: `docker compose -f ~/qwen-code-oai-proxy/docker-compose.yml restart`
4. Update locally: `nano .env.agent.secret`

---

## 📞 Quick Reference

| Service | Command | URL |
|---------|---------|-----|
| Backend | `ssh root@10.93.26.121` | http://10.93.26.121:42001 |
| Frontend | - | http://10.93.26.121:42002 |
| Swagger | - | http://10.93.26.121:42002/docs |
| Qwen API | `ssh root@10.93.26.121` | http://10.93.26.121:8080/v1 |

**Your Credentials:**
```
LMS_API_KEY=vanya630-lms-secret-key-2026
AUTOCHECKER_EMAIL=i.grishaev@innopolis.university
AUTOCHECKER_PASSWORD=vanya630yarunit
```

---

**Good luck! 🚀**
