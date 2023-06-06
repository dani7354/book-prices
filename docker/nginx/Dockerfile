FROM nginx:1.24.0-bullseye
EXPOSE 80
EXPOSE 443

COPY ./docker/nginx/nginx.conf /etc/nginx/nginx.conf

RUN rm -rf /usr/share/nginx/html/*
RUN mkdir /usr/share/nginx/html/static
RUN mkdir /etc/nginx/tls

COPY ./bookprices/web/assets /usr/share/nginx/html/static/assets