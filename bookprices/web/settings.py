import os

# DB settings
MYSQL_HOST = os.environ["MYSQL_SERVER"]
MYSQL_PORT = int(os.environ["MYSQL_SERVER_PORT"])
MYSQL_USER = os.environ["MYSQL_USER"]
MYSQL_PASSWORD = os.environ["MYSQL_PASSWORD"]
MYSQL_DATABASE = os.environ["MYSQL_DATABASE"]

# App settings
BOOK_PAGESIZE = 12
BOOK_IMAGES_PATH = "/static/images/books/"
BOOK_FALLBACK_IMAGE_NAME = "default.png"

AUTHOR_URL_PARAMETER = "author"
SEARCH_URL_PARAMETER = "search"
PAGE_URL_PARAMETER = "page"

FLASK_APP_PORT = int(os.environ.get("FLASK_APP_PORT", 3031))
DEBUG_MODE = os.environ.get("DEBUG", False)
