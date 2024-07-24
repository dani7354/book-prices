FROM python:3.12-alpine

ENV VENV_PATH=/opt/venv
RUN python3 -m venv "$VENV_PATH"
ENV PATH="$VENV_PATH/bin:$PATH"

WORKDIR /usr/local/bookprices_job
COPY ./bookprices bookprices
COPY ./docker/cronjob/requirements.txt requirements.txt
RUN pip install -r requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:/usr/local/bookprices_job"
RUN crontab ./bookprices/cronjob/crontab

CMD ["crond", "-f"]