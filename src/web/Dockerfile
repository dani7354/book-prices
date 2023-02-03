FROM python:3.11-slim-bullseye

EXPOSE 80
EXPOSE 443

WORKDIR /bookprices_web

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]