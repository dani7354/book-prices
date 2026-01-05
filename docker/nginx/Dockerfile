FROM nginx:1.29-trixie
EXPOSE 80
EXPOSE 443

RUN mkdir /etc/nginx/tls \
    && rm -rf /usr/share/nginx/html/* \
    && mkdir /usr/share/nginx/html/static

COPY ./docker/nginx/robots.txt /usr/share/nginx/html/static/robots.txt
COPY ./bookprices/web/assets /usr/share/nginx/html/static/assets

CMD ["nginx", "-g", "daemon off;"]