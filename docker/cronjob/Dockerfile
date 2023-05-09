FROM python:3.11-alpine

WORKDIR /usr/local/bookprices_job

COPY ./bookprices ./bookprices

COPY ./setup.py setup.py
COPY ./docker/cronjob/requirements.txt requirements.txt
RUN pip install -e .
RUN pip install -r requirements.txt

RUN mkdir ./config

RUN crontab ./bookprices/cronjob/crontab

CMD ["crond", "-f"]

