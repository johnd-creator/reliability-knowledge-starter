FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install

FROM node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ARG CEMS_COLLECTOR_API_BASE=http://cems-api:8003
ENV CEMS_COLLECTOR_API_BASE=$CEMS_COLLECTOR_API_BASE
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build
RUN addgroup -S app && adduser -S app -G app && chown -R app:app /app
USER app
EXPOSE 3000
CMD ["npm", "run", "start"]
