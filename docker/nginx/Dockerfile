FROM nginx:1.25-bullseye
EXPOSE 80
EXPOSE 443

RUN mkdir /etc/nginx/tls

RUN rm -rf /usr/share/nginx/html/*
RUN mkdir /usr/share/nginx/html/static
COPY ./docker/nginx/robots.txt /usr/share/nginx/html/static/robots.txt
COPY ./bookprices/web/assets /usr/share/nginx/html/static/assets
