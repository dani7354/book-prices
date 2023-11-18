FROM python:3.12-slim-bullseye
EXPOSE 3031

RUN apt-get update && apt-get install -y build-essential

RUN adduser --no-create-home bookprices
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