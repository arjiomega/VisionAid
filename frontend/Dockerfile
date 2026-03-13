# Stage 1: install dependencies
FROM node:22-alpine AS deps
WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

# Stage 2: build app
FROM node:22-alpine AS builder
WORKDIR /app

ARG NEXT_PUBLIC_BACKEND_BASE_URL
ARG NEXT_PUBLIC_BACKEND_BASE_WS_URL
ARG NEXT_PUBLIC_VLM_WS_ENDPOINT
ARG NEXT_PUBLIC_HEALTHCHECK_ENDPOINT
ARG NEXT_PUBLIC_AUTH_ENDPOINT

ENV NEXT_PUBLIC_BACKEND_BASE_URL=$NEXT_PUBLIC_BACKEND_BASE_URL
ENV NEXT_PUBLIC_BACKEND_BASE_WS_URL=$NEXT_PUBLIC_BACKEND_BASE_WS_URL
ENV NEXT_PUBLIC_VLM_WS_ENDPOINT=$NEXT_PUBLIC_VLM_WS_ENDPOINT
ENV NEXT_PUBLIC_HEALTHCHECK_ENDPOINT=$NEXT_PUBLIC_HEALTHCHECK_ENDPOINT
ENV NEXT_PUBLIC_AUTH_ENDPOINT=$NEXT_PUBLIC_AUTH_ENDPOINT

COPY --from=deps /app/node_modules ./node_modules
COPY . .

RUN npm run build

# Stage 3: production runner
FROM node:22-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production

COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/public ./public

EXPOSE 3000

CMD ["npm", "start"]