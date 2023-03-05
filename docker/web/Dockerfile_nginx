FROM python:3.11.2-slim-bullseye
EXPOSE 80

RUN apt-get update && apt-get install -y nginx build-essential

# Configure nginx
RUN adduser --no-create-home bookprices
COPY ./docker/web/nginx/bookprices /etc/nginx/sites-available/default
COPY ./docker/web/nginx/uwsgi_params /etc/nginx/uwsgi_params
RUN service nginx restart

WORKDIR /usr/local/bookprices_web

# move application files
COPY ./src/web web
COPY ./src/data data
COPY ./src/web/requirements.txt requirements.txt
COPY ./docker/web/bookprices_web.ini web/bookprices_web.ini

# install python dependencies
RUN pip3 install -r requirements.txt

WORKDIR /usr/local/bookprices_web/web
COPY ./docker/web/start.sh start.sh
RUN chmod +x start.sh

CMD ["./start.sh"]