# Стадия 1: Сборка приложения
FROM node:18-alpine AS builder
WORKDIR /app

# Определяем аргументы сборки
ARG VITE_SIM_API_URL
ARG VITE_AGENT_API_URL

# Устанавливаем переменные окружения для Vite
ENV VITE_SIM_API_URL=$VITE_SIM_API_URL
ENV VITE_AGENT_API_URL=$VITE_AGENT_API_URL

COPY package.json package-lock.json ./
RUN npm install --production=false
COPY . .
RUN npm run build || { echo "Build failed"; exit 1; }
RUN ls -la /app/dist # Для отладки

# Стадия 2: Продакшен
FROM nginx:stable
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
RUN chmod -R 755 /usr/share/nginx/html && ls -la /usr/share/nginx/html # Исправляем права
RUN touch /var/log/nginx/access.log /var/log/nginx/error.log && chmod 666 /var/log/nginx/* # Создаем лог-файлы
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]