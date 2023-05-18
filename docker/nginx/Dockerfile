FROM nginx:1.24.0-bullseye

COPY ./docker/nginx/default /etc/nginx/sites-available/default
COPY ./docker/nginx/uwsgi_params /etc/nginx/uwsgi_params

RUN mkdir /usr/share/nginx/html/static
RUN service nginx restart
