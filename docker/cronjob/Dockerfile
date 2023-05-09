FROM python:3.11-alpine

WORKDIR /usr/local/bookprices

COPY ./bookprices/cronjob ./cronjob
COPY ./bookprices/shared ./shared
COPY ./bookprices/tool ./tool

RUN pip install -r ./cronjob/requirements.txt
RUN mkdir ./cronjob/config

RUN crontab ./cronjob/crontab

CMD ["crond", "-f"]

