FROM python:3.13.1-slim-bullseye
EXPOSE 3031

RUN apt update \
    && apt upgrade -y \
    && apt install -y build-essential  \
    && apt clean  \
    && adduser --no-create-home bookprices

ENV VENV_PATH=/opt/venv
RUN python3 -m venv "$VENV_PATH"
ENV PATH="$VENV_PATH/bin:$PATH"

WORKDIR /usr/local/bookprices_web

COPY ./bookprices bookprices
COPY ./docker/web/bookprices_web.ini bookprices/web/bookprices_web.ini

COPY ./docker/web/requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt
ENV PYTHONPATH="/usr/local/bookprices_web/"

WORKDIR /usr/local/bookprices_web/bookprices/web

RUN mkdir -p ./log/uwsgi  \
    && chown -R bookprices:bookprices ./log

CMD ["uwsgi", "/usr/local/bookprices_web/bookprices/web/bookprices_web.ini"]