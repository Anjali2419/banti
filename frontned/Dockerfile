
# 1. Use Nginx lightweight base image
FROM nginx:alpine

# 2. Remove default Nginx website
RUN rm -rf /usr/share/nginx/html/*

# 3. Copy frontend files into Nginx web directory
COPY login.html register.html style.css /usr/share/nginx/html/

# 4. Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 5. Document the HTTP port
EXPOSE 80

# 6. Run Nginx in foreground
CMD ["nginx", "-g", "daemon off;"]
