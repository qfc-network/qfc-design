# Build from the demo/ directory so we can COPY both relay/ and public/.
#
#   cd qfc-design/demo
#   docker build -f relay/Dockerfile -t qfc-demo-relay .
#
FROM node:20-alpine AS build
WORKDIR /app
COPY relay/package.json ./
RUN npm install --no-audit --no-fund --omit=dev

FROM node:20-alpine
WORKDIR /app
ENV NODE_ENV=production
COPY --from=build /app/node_modules ./node_modules
COPY relay/server.js ./server.js
COPY public ./public
# Relay serves ../public relative to cwd; adjust if you change layout
ENV QFC_DEMO_STATIC_DIR=./public
EXPOSE 3290
USER node
CMD ["node", "server.js"]
