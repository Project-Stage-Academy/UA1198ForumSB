FROM nginx

COPY ./config/nginx.conf /etc/nginx/nginx.conf
#COPY ./config/websocket_settings.conf /etc/nginx/websocket_settings.conf
#COPY ./config/cors_headers.conf /etc/nginx/cors_headers.conf

CMD ["nginx", "-g", "daemon off;"]
