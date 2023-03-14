FROM python:3.11-alpine

WORKDIR /usr/local/book_prices

COPY ./src/book_source ./book_source
COPY ./src/configuration ./configuration
COPY ./src/data ./data
COPY ./src/cronjobs ./cronjobs

RUN pip install -r ./cronjobs/requirements.txt
RUN mkdir ./cronjobs/config

RUN crontab ./cronjobs/crontab

CMD ["crond", "-f"]