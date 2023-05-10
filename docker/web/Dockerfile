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
COPY ./bookprices bookprices
COPY ./docker/web/bookprices_web.ini bookprices/web/bookprices_web.ini


# install python dependencies
COPY ./setup.py setup.py
COPY ./docker/web/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN pip3 install -e .

WORKDIR /usr/local/bookprices_web/bookprices/web
COPY ./docker/web/start.sh start.sh
RUN chmod +x start.sh

CMD ["./start.sh"]