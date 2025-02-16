FROM python:3.13-alpine

ENV VENV_PATH=/opt/venv
RUN python3 -m venv "$VENV_PATH"
ENV PATH="$VENV_PATH/bin:$PATH"

RUN mkdir -p /app/logs
WORKDIR /app
COPY ./bookprices/shared bookprices/shared
COPY ./bookprices/job bookprices/job
COPY ./docker/jobscheduler/requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

ENV PYTHONPATH="/app"

CMD ["python3", "bookprices/job/start_jobscheduler.py"]