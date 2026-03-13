### 1.10. Set up the environment (on your laptop)

1. Go to `VS Code Terminal`, [check that the current directory is `se-toolkit-lab-6`](../../wiki/shell.md#check-the-current-directory-is-directory-name), and install `Python` dependencies:

   ```terminal
   uv sync --dev
   ```

2. Create the environment file:

   ```terminal
   cp .env.docker.example .env.docker.secret
   ```

3. Configure the autochecker API credentials.

   The ETL pipeline fetches data from the autochecker dashboard API.
   Open `.env.docker.secret` and set:

   ```text
   AUTOCHECKER_EMAIL=<your-email>@innopolis.university
   AUTOCHECKER_PASSWORD=<your-github-username><your-telegram-alias>
   ```

   Example: if your GitHub username is `johndoe` and your Telegram alias is `jdoe`, the password is `johndoejdoe`.

   > [!IMPORTANT]
   > The credentials must match your autochecker bot registration.

### 1.11. Clean up the previous lab (on your VM)

> [!IMPORTANT]
> Remove previous lab containers and volumes to free up ports and disk space on your VM.

1. [Connect to your VM](../../wiki/vm.md#connect-to-the-vm).
2. Navigate to the previous lab's project directory:

   ```terminal
   cd ~/se-toolkit-lab-5
   ```

3. Stop and remove all containers and volumes:

   ```terminal
   docker compose --env-file .env.docker.secret down -v
   ```

4. Go back to the home directory:

   ```terminal
   cd ~
   ```

> [!NOTE]
> If you didn't do Lab 5, try `cd ~/se-toolkit-lab-4` instead.
> If neither directory exists, skip this step.

### 1.12. Deploy to your VM

#### 1.12.1. Connect to your VM and clone the repo

1. Connect to your VM:

   ```terminal
   ssh <vm-user>@<vm-ip>
   ```

   If unable, see [how to connect to your VM](../../wiki/vm.md#connect-to-the-vm).

2. Clone your fork on the VM:

   ```terminal
   cd ~
   git clone https://github.com/<your-github-username>/se-toolkit-lab-6.git
   cd se-toolkit-lab-6
   ```

#### 1.12.2. Prepare the environment (on the VM)

1. Create the `Docker` environment file:

   ```terminal
   cp .env.docker.example .env.docker.secret
   ```

2. Edit `.env.docker.secret`:

   ```terminal
   nano .env.docker.secret
   ```

   Set your autochecker API credentials:

   ```text
   AUTOCHECKER_EMAIL=<your-email>@innopolis.university
   AUTOCHECKER_PASSWORD=<your-github-username><your-telegram-alias>
   ```

   Set `LMS_API_KEY` — this is the **backend API key** that protects your LMS endpoints (used for `Authorization: Bearer` in Swagger and the frontend). It is **not** the LLM key — that comes later in Task 1.

   ```text
   LMS_API_KEY=set-it-to-something-and-remember-it
   ```

   Save and exit: `Ctrl+X`, then `y`, then `Enter`.

#### 1.12.3. Start the services (on the VM)

1. Start the services in the background:

   ```terminal
   docker compose --env-file .env.docker.secret up --build -d
   ```

2. Check that the containers are running:

   ```terminal
   docker compose --env-file .env.docker.secret ps --format "table {{.Service}}\t{{.Status}}"
   ```

   You should see all four services running:

   ```terminal
   SERVICE    STATUS
   app        Up 50 seconds
   caddy      Up 49 seconds
   pgadmin    Up 50 seconds
   postgres   Up 55 seconds (healthy)
   ```

   <details><summary><b>Troubleshooting (click to open)</b></summary>

   <h4>Port conflict (<code>port is already allocated</code>)</h4>

   [Clean up `Docker`](../../wiki/docker.md#clean-up-docker), then run the `docker compose up` command again.

   <h4>Containers exit immediately</h4>

   Rebuild all containers from scratch:

   ```terminal
   docker compose --env-file .env.docker.secret down -v
   docker compose --env-file .env.docker.secret up --build -d
   ```

   <h4>Image pull fails</h4>

   Check your internet connection. If you are behind a proxy, configure `Docker` to use it.

   </details>

### 1.13. Populate the database

The database starts empty. You need to run the ETL pipeline to populate it with data from the autochecker API.

1. Open in a browser: `http://<your-vm-ip>:42002/docs`

   You should see the Swagger UI page.

2. [Authorize in Swagger](../../wiki/swagger.md#authorize-in-swagger-ui) with the `LMS_API_KEY` you set in `.env.docker.secret`.

3. Run the ETL sync by calling `POST /pipeline/sync` in Swagger UI.

   You should get a response showing the number of items and logs loaded:

   ```json
   {
     "items_loaded": 120,
     "logs_loaded": 5000
   }
   ```

   > [!NOTE]
   > The exact numbers depend on how much data the autochecker API has.
   > As long as both numbers are greater than 0, the sync worked.

4. Verify data by calling `GET /items/`.

   You should get a non-empty array of items.

### 1.14. Verify the deployment

1. Open `http://<your-vm-ip>:42002/docs` in a browser.

   You should see the Swagger UI with all endpoints.

2. Open `http://<your-vm-ip>:42002/` in a browser.

   You should see the frontend. Enter your API key to connect.

3. Switch to the **Dashboard** tab.

   You should see charts with analytics data (score distribution, submissions timeline, group performance, task pass rates).

> [!IMPORTANT]
> If the dashboard shows no data or errors, make sure:
>
> - The ETL sync completed successfully (step 1.13)
> - You entered the correct API key in the frontend
> - Try selecting a different lab in the dropdown (e.g., `lab-04`)

### 1.15. Set up a coding agent

A coding agent can help you write code, explain concepts, and debug issues.

- Method 1: [Set up a `Qwen Code`-based agent](../../wiki/qwen.md#set-up-the-qwen-code-local-machine).
- Method 2: [Choose another coding agent](../../wiki/coding-agents.md#choose-and-use-a-coding-agent).