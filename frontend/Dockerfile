# Stage 1: Build the React frontend
FROM node:25-alpine AS builder

WORKDIR /app

COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm
RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm install --frozen-lockfile

COPY . .
RUN pnpm run build


# Stage 2: Serve with Caddy
FROM caddy:2.11-alpine

COPY --from=builder /app/dist /srv