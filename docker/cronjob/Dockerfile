FROM python:3.12-alpine

WORKDIR /usr/local/bookprices_job

COPY ./bookprices bookprices

COPY ./setup.py setup.py
COPY ./docker/cronjob/requirements.txt requirements.txt
RUN pip install -r requirements.txt
ENV PYTHONPATH "${PYTHONPATH}:/usr/local/bookprices_job"

# create directory for config
RUN mkdir ./config

RUN crontab ./bookprices/cronjob/crontab

CMD ["crond", "-f"]
