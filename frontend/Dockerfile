# Stage 1: Build Vite static assets
FROM node:20-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
# No VITE_API_BASE_URL needed — frontend uses relative /api/ paths
# so NGINX handles the proxy inside the container network.
RUN npm run build

# Stage 2: Serve via NGINX
FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
