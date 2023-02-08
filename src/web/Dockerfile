FROM python:3.11-slim-bullseye
EXPOSE 5000

WORKDIR /bookprices_web

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN pip3 install flask

COPY ./web web
COPY ./data data

WORKDIR /bookprices_web/web

CMD [ "python3", "-m" , "flask", "--app", "app.py", "run", "--host=0.0.0.0"]


