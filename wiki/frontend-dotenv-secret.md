# `frontend/.env.secret`

<h2>Table of contents</h2>

- [What is `frontend/.env.secret`](#what-is-frontendenvsecret)
- [`VITE_API_TARGET`](#vite_api_target)

## What is `frontend/.env.secret`

`frontend/.env.secret` is an [`.env` file](./environments.md#env-file) that stores [environment variables](./environments.md#environment-variable) for the `Vite` dev server.

`Vite` loads the values when running `pnpm run dev`.

Docs:

- [Vite env and mode](https://vite.dev/guide/env-and-mode)

Default values: [`frontend/.env.example`](../frontend/.env.example)

> [!NOTE]
> It was added to [`.gitignore`](./git.md#gitignore) because you may specify there
> [secrets](./environments.md#secrets) such as the [address of your VM](./vm.md#your-vm-ip-address).

> [!TIP]
> No edits are needed for local development.
> The default values in [`frontend/.env.example`](../frontend/.env.example) work out of the box.

## `VITE_API_TARGET`

The URL of the back-end API that the `Vite` dev server proxies requests to.

Default: `http://127.0.0.1:42002`

The default points to the [`Caddy`](./caddy.md#what-is-caddy) reverse proxy running via [`Docker Compose`](./docker-compose.md#what-is-docker-compose) on your local machine.

Change this to `http://<your-vm-ip-address>:<caddy-port>` if the API runs on the VM. See [`<your-vm-ip-address>`](./vm.md#your-vm-ip-address) and [`CADDY_HOST_PORT`](./dotenv-docker-secret.md#caddy_host_port) in [`.env.docker.secret`](./dotenv-docker-secret.md#what-is-envdockersecret).
