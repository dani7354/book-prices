FROM python:3.11-slim-bullseye

WORKDIR /usr/local/price_updater

COPY ../src ./
COPY ../requirements.txt ./

RUN pip install -r requirements.txt

ENTRYPOINT [ "python3", "./update_prices.py", "-c", "./config/config.json"]