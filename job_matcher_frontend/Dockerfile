FROM node:18-alpine AS build

WORKDIR /app

COPY package*.json ./

RUN npm install

ENV VITE_API_URL=/api

COPY . .
RUN npm run build

# serve with nginx
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
CMD ["nginx", "-g", "daemon off;"]