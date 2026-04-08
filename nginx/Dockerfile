FROM nginx:1.25-alpine

# Remove default config
RUN rm /etc/nginx/nginx.conf

# Copy custom config as main config
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
