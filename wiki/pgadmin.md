# `pgAdmin`

<h2>Table of contents</h2>

- [What is `pgAdmin`](#what-is-pgadmin)
- [`<pgadmin-port>`](#pgadmin-port)
- [Open `pgAdmin`](#open-pgadmin)
- [Manage `PostgreSQL` servers](#manage-postgresql-servers)
  - [Connect to the `PostgreSQL` server](#connect-to-the-postgresql-server)
  - [Delete the `PostgreSQL` server](#delete-the-postgresql-server)
- [`Object Explorer`](#object-explorer)
  - [Open the database](#open-the-database)
  - [Open schemas in the database](#open-schemas-in-the-database)
  - [Open tables in the database](#open-tables-in-the-database)
  - [Browse data in the table](#browse-data-in-the-table)
  - [Browse columns in the table](#browse-columns-in-the-table)
- [`Query Tool`](#query-tool)
  - [Open the `Query Tool`](#open-the-query-tool)
  - [Run the query](#run-the-query)
  - [Copy the query data output](#copy-the-query-data-output)
  - [Save to file the query data output](#save-to-file-the-query-data-output)
- [`ERD Tool`](#erd-tool)
  - [Open the ERD for the database](#open-the-erd-for-the-database)
  - [View the ERD in crow's foot notation](#view-the-erd-in-crows-foot-notation)
  - [View the ERD in Chen notation](#view-the-erd-in-chen-notation)

## What is `pgAdmin`

`pgAdmin` is a web-based graphical tool for managing `PostgreSQL` databases.

Docs:

- [Official PgAdmin docs](https://www.pgadmin.org/docs/)

## `<pgadmin-port>`

The [port number](./computer-networks.md#port-number) (without `<` and `>`) which `pgAdmin` [listens on](./computer-networks.md#listen-on-a-port).

The port number is the value of [`PGADMIN_HOST_PORT`](./dotenv-docker-secret.md#pgadmin_host_port) in [`.env.docker.secret`](./dotenv-docker-secret.md#what-is-envdockersecret).

## Open `pgAdmin`

> [!NOTE]
> The default values are defined in [`.env.docker.example`](../.env.docker.example).
>
> The actual values are in `.env.docker.secret`.

1. Open `http://<address>:<pgadmin-port>` in a browser. Replace:
   - `<address>` with:
     - [`localhost`](./computer-networks.md#localhost) if you deployed on your local machine.
     - [`<your-vm-ip-address>`](vm.md#your-vm-ip-address) if you deployed on [your VM](./vm.md#your-vm);
   - [`<pgadmin-port>`](#pgadmin-port).
2. Log in with the credentials from `.env.docker.secret`:
   - `Email`: the value of `PGADMIN_EMAIL` (default: `admin@example.com`).
   - `Password`: the value of `PGADMIN_PASSWORD` (default: `admin`).

<!-- TODO servers.json -->

## Manage `PostgreSQL` servers

Actions:

- [Connect to the `PostgreSQL` server](#connect-to-the-postgresql-server)
- [Delete the `PostgreSQL` server](#delete-the-postgresql-server)

### Connect to the `PostgreSQL` server

> [!NOTE]
> The environment variables are defined in the [`.env.docker.secret`](./dotenv-docker-secret.md#what-is-envdockersecret) file that you used to deploy the [`pgadmin` service](./docker-compose-yml.md#pgadmin-service).

1. [Open `pgAdmin`](#open-pgadmin).
2. Right-click `Servers` in the left panel.
3. Click `Register` -> `Server...`.
4. In the `General` tab:
   - `Name`: the value of [`CONST_POSTGRESQL_SERVER_NAME`](./dotenv-docker-secret.md#const_postgresql_server_name).
5. In the `Connection` tab:
   - `Host name/address`: the value of [`CONST_POSTGRESQL_SERVICE_NAME`](./dotenv-docker-secret.md#const_postgresql_service_name) (see [`Docker Compose` networking](./docker-compose.md#docker-compose-networking)).
   - `Port`: the value of [`CONST_POSTGRESQL_DEFAULT_PORT`](./dotenv-docker-secret.md#const_postgresql_default_port).
   - `Maintenance database`: the value of [`POSTGRES_DB`](./dotenv-docker-secret.md#postgres_db).
   - `Username`: the value of [`POSTGRES_USER`](./dotenv-docker-secret.md#postgres_user).
   - `Password`: the value of [`POSTGRES_PASSWORD`](./dotenv-docker-secret.md#postgres_password).
6. Click `Save`.

   You should see the server in the [`Object Explorer`](./pgadmin.md#object-explorer):

   <img alt="Object explorer and server" src="./images/pgadmin/object-explorer-server.png" style="width:300px">

### Delete the `PostgreSQL` server

<!-- TODO -->

## `Object Explorer`

Actions:

<!-- no toc -->
- [Open the database](#open-the-database)
- [Open schemas in the database](#open-schemas-in-the-database)
- [Open tables in the database](#open-tables-in-the-database)
- [Browse data in the table](#browse-data-in-the-table)
- [Browse columns in the table](#browse-columns-in-the-table)

### Open the database

> [!NOTE]
> The `<db-name>` is the name of the database which you want to open.

1. Expand `Servers`.
2. Expand `<server-name>`.
3. Expand `Databases`.
4. Expand `<db-name>`.

### Open schemas in the database

> [!NOTE]
> See [database schema](./database.md#database-schema).

> [!NOTE]
> The `<db-name>` is the name of the database where you want to see schemas.

1. [Open the database `<db-name>`](#open-the-database).
2. Expand `Schemas`.

### Open tables in the database

> [!NOTE]
> The `<db-name>` is the name of the database where you want to open tables.

1. [Open schemas in the database `<db-name>`](#open-schemas-in-the-database).
2. Expand `public`.
3. Expand `Tables`.

### Browse data in the table

> [!NOTE]
> The `<db-name>` is the name of the database where you want to browse tables.
>
> The `<table-name>` is the name of the table that you want to inspect.

1. [Open tables in the database `<db-name>`](#open-tables-in-the-database).
2. Right-click `<table-name>`.
3. Click `View/Edit Data`.
4. Click `All Rows`.

### Browse columns in the table

> [!NOTE]
> The `<db-name>` is the name of the database that has the table `<table-name>`.
>
> The `<table-name>` is the name of the table whose columns you want to inspect.

1. [Open tables in the database `<db-name>`](#open-tables-in-the-database).
2. Right-click `<table-name>`.
3. Click `Properties`.
4. Click `Columns`.

## `Query Tool`

Docs:

- [Query Tool](https://www.pgadmin.org/docs/pgadmin4/9.12/query_tool.html)

Actions:

<!-- no toc -->
- [Open the `Query Tool`](#open-the-query-tool).
- [Run the query](#run-the-query).
- [Copy the query data output](#copy-the-query-data-output)

### Open the `Query Tool`

> [!NOTE]
> The `<db-name>` is the name of the database that you want to run [`SQL` queries](./sql.md#sql-query) against.

1. [Open the database `<db-name>`](#open-the-database).
2. Right-click `<db-name>`.
3. Click `Query Tool`.

### Run the query

> [!NOTE]
> The `<db-name>` is the name of the database that you run the [`SQL` query](./sql.md#sql-query) against.

1. [Open the `Query Tool` for the database `<db-name>`](#open-the-query-tool).
2. Write your `SQL` query, e.g.:

   ```sql
   SELECT tablename FROM pg_tables WHERE schemaname = 'public';
   ```

3. Click `Execute Script`.

   <img alt="Execute script" src="./images/pgadmin/execute-script.png" style="width:300px">

   In the `Data Output` tab, you should see a table with the data returned by the query:

   <img alt="Query data output tab" src="./images/pgadmin/query-data-output-tab.png" style="width:300px">

   In the `Messages` tab, you should see the text report about your query.

   <img alt="Query messages tab" src="./images/pgadmin/query-messages-tab.png" style="width:300px">

### Copy the query data output

> [!NOTE]
> The `<db-name>` is the name of the database that you run the [`SQL` query](./sql.md#sql-query) against.

1. [Run the query against the database `<db-name>`](#run-the-query).
2. Open the `Data Output` tab.
3. Click the upper-left corner in the `Data Output` tab to select the full table.

   <img alt="Data Output - select all" src="./images/pgadmin/data-output-select-all.png" style="width:400px">
4. Click `Copy` to copy the full table to the clipboard.

   <img alt="Data Output - select all" src="./images/pgadmin/data-output-copy.png" style="width:400px">

### Save to file the query data output

> [!NOTE]
> The `<db-name>` is the name of the database that you run the [`SQL` query](./sql.md#sql-query) against.

1. [Run the query against the database `<db-name>`](#run-the-query).
2. Open the `Data Output` tab.
3. Click `Save results to file`.

   <img alt="Data output - save results to file" src="./images/pgadmin/data-output-save-results-to-file.png" style="width:400px">

   A comma-separated [`CSV`](./file-formats.md#csv) file should be downloaded.

## `ERD Tool`

Docs:

- [ERD Tool](https://www.pgadmin.org/docs/pgadmin4/9.12/erd_tool.html)

Actions:

- [Open the ERD for the database](#open-the-erd-for-the-database)
- View the ERD in a specific notation:
  - Option 1: [View the ERD in crow's foot notation](#view-the-erd-in-crows-foot-notation).
  - Option 2: [View the ERD in Chen notation](#view-the-erd-in-chen-notation).

### Open the ERD for the database

> [!NOTE]
> See [ERD](./database-modeling.md#erd).

1. [Open the database `<db-name>`](#open-the-database).
2. Right-click the `<db-name>`.
3. Click `ERD for Database`.

### View the ERD in crow's foot notation

> [!NOTE]
> See [ERD in crow's foot notation](./database-modeling.md#erd-in-crows-foot-notation).

1. [Open the ERD for the database `<db-name>`](#open-the-erd-for-the-database).
2. Click `Cardinality Notation`.
3. Click `Crow's Foot Notation`.

   You should see an ERD like this:

   <img alt="ERD in crow's foot notation" src="./images/pgadmin/erd-crows-foot.png" style="width:400px">

### View the ERD in Chen notation

> [!NOTE]
> See [ERD in Chen notation](./database-modeling.md#erd-in-chen-notation).

1. [Open the ERD for the database `<db-name>`](#open-the-erd-for-the-database).
2. Click `Cardinality Notation`.
3. Click `Chen Notation`.

   You should see an ERD like this:

   <img alt="ERD in Chen notation" src="./images/pgadmin/erd-chen.png" style="width:400px">
