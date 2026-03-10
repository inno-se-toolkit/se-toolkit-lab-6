# Grafana Dashboard

<h4>Time</h4>

~30 min

<h4>Purpose</h4>

Set up `Grafana` as an alternative dashboard tool, connect it to `PostgreSQL`, and build visualizations using `SQL` queries.

<h4>Context</h4>

In the required tasks, you built a custom dashboard with `Chart.js` inside the `React` front-end. `Grafana` is a dedicated dashboarding tool used in industry for monitoring and analytics — it connects directly to the database and lets you build dashboards without writing front-end code.

<h4>Diagram</h4>

```mermaid
sequenceDiagram
    actor Developer
    participant GH as GitHub
    participant VM as VM<br/>(Docker)
    participant Grafana as Grafana<br/>(browser)
    participant PG as PostgreSQL<br/>(Docker)

    Developer->>GH: Create Lab Task issue
    Developer->>VM: Uncomment Grafana service
    Developer->>VM: docker compose up --build -d
    Developer->>Grafana: Log in
    Developer->>Grafana: Add PostgreSQL data source
    Grafana->>PG: Test connection
    PG-->>Grafana: Connection OK
    Developer->>Grafana: Build dashboard with SQL panels
    Grafana->>PG: Execute SQL queries
    PG-->>Grafana: Query results
    Developer->>GH: Write reflection comment
    Developer->>GH: Close the issue
```

<h4>Table of contents</h4>

- [1. Steps](#1-steps)
  - [1.1. Create a `Lab Task` issue](#11-create-a-lab-task-issue)
  - [1.2. Enable `Grafana` in `Docker Compose`](#12-enable-grafana-in-docker-compose)
  - [1.3. Start `Grafana`](#13-start-grafana)
  - [1.4. Add the `PostgreSQL` data source](#14-add-the-postgresql-data-source)
  - [1.5. Build a dashboard](#15-build-a-dashboard)
  - [1.6. Reflection](#16-reflection)
  - [1.7. Finish the task](#17-finish-the-task)
  - [1.8. Check the task using the autochecker](#18-check-the-task-using-the-autochecker)
- [2. Acceptance criteria](#2-acceptance-criteria)

## 1. Steps

### 1.1. Create a `Lab Task` issue

Title: `[Task] Grafana Dashboard`

### 1.2. Enable `Grafana` in `Docker Compose`

1. [Open the file](../../../wiki/vs-code.md#open-the-file):
   [`docker-compose.yml`](../../../docker-compose.yml).

2. Find the commented-out `grafana` service at the bottom.

3. Uncomment the entire `grafana` service block (remove the `#` characters at the start of each line).

4. If you want to change the default admin credentials, uncomment and edit the `GF_SECURITY_ADMIN_USER` and `GF_SECURITY_ADMIN_PASSWORD` lines in [`.env.docker.secret`](../../../wiki/dotenv-docker-secret.md#what-is-envdockersecret).

### 1.3. Start `Grafana`

1. To start `Grafana` on your VM,

   [run in the `VS Code Terminal`](../../../wiki/vs-code.md#run-a-command-in-the-vs-code-terminal):

   ```terminal
   cd se-toolkit-lab-5
   docker compose --env-file .env.docker.secret up --build -d
   ```

2. Open in a browser: `http://<your-vm-ip-address>:3000`.

   Replace [`<your-vm-ip-address>`](../../../wiki/vm.md#your-vm-ip-address).

3. Log in with the default credentials:
   - Username: `admin`
   - Password: `admin`

   You will be prompted to change the password on first login.

### 1.4. Add the `PostgreSQL` data source

1. In `Grafana`, go to **Connections** > **Data sources** > **Add data source**.
2. Select **PostgreSQL**.
3. Configure the connection:

   | Field        | Value           |
   | ------------ | --------------- |
   | Host         | `postgres:5432` |
   | Database     | `db-lab-5`      |
   | User         | `postgres`      |
   | Password     | `postgres`      |
   | TLS/SSL Mode | `disable`       |

   > 🟦 **Note**
   >
   > `Grafana` connects to `PostgreSQL` through the `Docker` network.
   > The hostname `postgres` is the service name from [`docker-compose.yml`](../../../docker-compose.yml).

4. Click **Save & test**. You should see a "Database Connection OK" message.

### 1.5. Build a dashboard

1. Go to **Dashboards** > **New** > **New dashboard**.
2. Add at least two panels. Example ideas:

   **Panel 1: Score distribution**

   Query:

   ```sql
   SELECT
     CASE
       WHEN score BETWEEN 0 AND 25 THEN '0-25'
       WHEN score BETWEEN 26 AND 50 THEN '26-50'
       WHEN score BETWEEN 51 AND 75 THEN '51-75'
       WHEN score BETWEEN 76 AND 100 THEN '76-100'
     END AS bucket,
     COUNT(*) AS count
   FROM interacts
   WHERE score IS NOT NULL
   GROUP BY bucket
   ORDER BY bucket;
   ```

   Visualization: Bar chart.

   **Panel 2: Submissions over time**

   Query:

   ```sql
   SELECT
     DATE(created_at) AS date,
     COUNT(*) AS submissions
   FROM interacts
   GROUP BY DATE(created_at)
   ORDER BY date;
   ```

   Visualization: Time series or line chart.

3. Save the dashboard.

### 1.6. Reflection

Write a comment on your issue comparing the two approaches:

1. **Hand-built dashboard** (`React` + `Chart.js`): What was hard? What was easy?
2. **Tool-assisted dashboard** (`Grafana`): What was hard? What was easy?
3. When would you choose one approach over the other?

### 1.7. Finish the task

1. Close the issue.

### 1.8. Check the task using the autochecker

[Check the task using the autochecker `Telegram` bot](../../../wiki/autochecker.md#check-the-task-using-the-autochecker-bot).

---

## 2. Acceptance criteria

- [ ] Issue has the correct title.
- [ ] `Grafana` is accessible on port `3000`.
- [ ] The dashboard has at least 2 panels with data from `PostgreSQL`.
- [ ] The issue contains a reflection comment comparing the two dashboard approaches.
- [ ] Issue is closed.
