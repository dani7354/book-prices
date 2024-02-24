import os

# DB settings
MYSQL_HOST = os.environ["MYSQL_SERVER"]
MYSQL_PORT = int(os.environ["MYSQL_SERVER_PORT"])
MYSQL_USER = os.environ["MYSQL_USER"]
MYSQL_PASSWORD = os.environ["MYSQL_PASSWORD"]
MYSQL_DATABASE = os.environ["MYSQL_DATABASE"]

# Cache settings
REDIS_SERVER = os.environ.get("REDIS_SERVER")
REDIS_SERVER_PORT = int(os.environ.get("REDIS_SERVER_PORT", "6379"))
REDIS_DB = int(os.environ.get("REDIS_DB", "0"))
CACHE_DEFAULT_TIMEOUT = int(os.environ.get("CACHE_DEFAULT_TIMEOUT", "300"))

# Google settings
GOOGLE_CLIENT_SECRETS_FILE = os.environ["GOOGLE_CLIENT_SECRETS_FILE"]
GOOGLE_OAUTH_REDIRECT_URI = os.environ["GOOGLE_OAUTH_REDIRECT_URI"]

# App settings
DEBUG_MODE = os.environ.get("DEBUG", "False") == "True"
SITE_HOSTNAME = "bogpriser.stuhrs.dk"

BOOK_PAGESIZE = 20
BOOK_IMAGES_PATH = "/static/assets/images/books/" if DEBUG_MODE else "/static/images/books/"
BOOK_FALLBACK_IMAGE_NAME = "default.png"

AUTHOR_URL_PARAMETER = "author"
SEARCH_URL_PARAMETER = "search"
ORDER_BY_URL_PARAMETER = "orderby"
PAGE_URL_PARAMETER = "page"
DESCENDING_URL_PARAMETER = "descending"
GOOGLE_AUTH_ERROR_URL_PARAMETER = "error"
GOOGLE_AUTH_CODE_URL_PARAMETER = "code"

FLASK_SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "supersecretkey")
FLASK_APP_PORT = int(os.environ.get("FLASK_APP_PORT", 3031))
