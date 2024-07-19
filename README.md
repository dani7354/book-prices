# book-prices
A Flask web application for comparing book prices from selected Danish webshops. An instance is running at 
[https://bogpriser.stuhrs.dk](https://bogpriser.stuhrs.dk/) (Unavailable at the moment).

## Setup
1. Clone the repository
2. Set environment variables in .env files for the web, cronjob and db containers (examples are to be found in `docker/`)
3. Create missing directories for the mounted volumes in `docker-compose.yaml`
4. Run `docker-compose --profile default up`