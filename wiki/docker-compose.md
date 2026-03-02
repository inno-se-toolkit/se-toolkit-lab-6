# `Docker Compose`

<h2>Table of contents</h2>

- [What is `Docker Compose`](#what-is-docker-compose)
- [Service](#service)
  - [Service name](#service-name)
- [`Docker Compose` networking](#docker-compose-networking)
- [Volume](#volume)
- [Actions](#actions)
  - [Stop and remove all containers](#stop-and-remove-all-containers)
  - [Stop and remove all containers and volumes](#stop-and-remove-all-containers-and-volumes)
- [Stop and remove all containers, volumes, and images](#stop-and-remove-all-containers-volumes-and-images)

## What is `Docker Compose`

`Docker Compose` runs multi-container apps from a `docker-compose.yml` file.

Example of the file: [`docker-compose.yml`](../docker-compose.yml).

See also:

- [`Docker`](./docker.md) for general `Docker` concepts ([images](./docker.md#image), [containers](./docker.md#container), [volumes](./docker.md#volume), [health checks](./docker.md#health-checks), etc.).

## Service

<!-- TODO -->

### Service name

<!-- TODO -->

## `Docker Compose` networking

`Docker Compose` creates a [network](./computer-networks.md#what-is-a-network) where [services](#service) can reach each other by their [service name](#service-name).

Docs:

- [Networking in Compose](https://docs.docker.com/compose/how-tos/networking/)

## Volume

## Actions

<!-- TODO all - not globally -->

### Stop and remove all containers

1. To stop all running [services](#service) and remove [containers](./docker.md#container),

   [run in the `VS Code Terminal`](../../wiki/vs-code.md#run-a-command-in-the-vs-code-terminal):

   ```terminal
   docker compose --env-file .env.docker.secret down
   ```

### Stop and remove all containers and volumes

1. To stop all running [services](#service), remove [containers](./docker.md#container), and remove [volumes](./docker.md#volume),

   [run in the `VS Code Terminal`](../../wiki/vs-code.md#run-a-command-in-the-vs-code-terminal):

   ```terminal
   docker compose --env-file .env.docker.secret down -v
   ```

## Stop and remove all containers, volumes, and images

1. To stop all running [services](#service), remove [containers](./docker.md#container), remove [volumes](./docker.md#volume), and remove [images](./docker.md#image),

   [run in the `VS Code Terminal`](./vs-code.md#run-a-command-in-the-vs-code-terminal):

   ```terminal
   docker compose --env-file .env.docker.secret down -v --rmi all
   ```
