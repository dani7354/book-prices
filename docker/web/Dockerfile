FROM python:3.12-slim-bullseye
EXPOSE 3031

RUN apt-get update  \
    && apt-get install -y build-essential  \
    && apt-get clean  \
    && adduser --no-create-home bookprices

ENV VENV_PATH=/opt/venv
RUN python3 -m venv "$VENV_PATH"
ENV PATH="$VENV_PATH/bin:$PATH"

WORKDIR /usr/local/bookprices_web

COPY ./bookprices bookprices
COPY ./docker/web/bookprices_web.ini bookprices/web/bookprices_web.ini

COPY ./docker/web/requirements.txt requirements.txt
RUN pip install -r requirements.txt
ENV PYTHONPATH "${PYTHONPATH}:/usr/local/bookprices_web/"

WORKDIR /usr/local/bookprices_web/bookprices/web

RUN mkdir -p ./log/uwsgi  \
    && chown -R bookprices:bookprices ./log

CMD ["uwsgi", "/usr/local/bookprices_web/bookprices/web/bookprices_web.ini"]