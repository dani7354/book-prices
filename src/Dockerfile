FROM python:3.11-alpine

WORKDIR /usr/local/price_updater

COPY . ./
RUN pip install -r ./requirements.txt
RUN mkdir ./config

RUN crontab crontab

CMD ["crond", "-f"]