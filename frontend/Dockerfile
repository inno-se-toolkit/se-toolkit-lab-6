# Stage 1: Build the React frontend
# A portable solution: download image from Docker Hub.
# FROM node:22-alpine AS builder

# A less portable solution: download image through a cache proxy provided by the University.
# This solution is necessary to avoid "Too many requests" errors.
# This solution won't work outside the University network.
FROM harbor.pg.innopolis.university/docker-hub-cache/node:22-alpine AS builder

WORKDIR /app

COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile

COPY . .
RUN pnpm run build


# Stage 2: Serve with Caddy
# A portable solution: download image from Docker Hub.
# FROM caddy:2.11-alpine

# A less portable solution: download image through a cache proxy provided by the University.
# This solution is necessary to avoid "Too many requests" errors.
# This solution won't work outside the University network.
FROM harbor.pg.innopolis.university/docker-hub-cache/caddy:2.11-alpine

COPY --from=builder /app/dist /srv
