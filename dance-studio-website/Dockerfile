# Stage 1: Build the Vue.js application
FROM node:20-alpine as builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .
RUN npm run build

# Stage 2: Serve the application with Nginx
FROM node:20-alpine

WORKDIR /app

COPY --from=builder /app/dist .

RUN npm install -g serve

EXPOSE 80

CMD ["serve", "-s", ".", "-l", "80"]
