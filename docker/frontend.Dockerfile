FROM node:20-alpine as build

WORKDIR /app

COPY frontend/package.json ./
RUN npm install

COPY frontend/ ./

RUN npm run build
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html

# Configure nginx to handle SPA routing
RUN echo 'server { \
    listen 80; \
    location / { \
        root /usr/share/nginx/html; \
        index index.html; \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]