FROM python:3.11-alpine

WORKDIR /usr/local/price_updater

COPY ./src/book_source ./book_source
COPY ./src/configuration ./configuration
COPY ./src/data ./data
COPY ./src/crontab ./crontab
COPY ./src/requirements.txt requirements.txt
COPY ./src/update_prices.py ./update_prices.py

RUN pip install -r ./requirements.txt
RUN mkdir ./config

RUN crontab crontab

CMD ["crond", "-f"]