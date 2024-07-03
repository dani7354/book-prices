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
GOOGLE_API_SCOPES = ["https://www.googleapis.com/auth/userinfo.email", "openid"]

# App settings
DEBUG_MODE = os.environ.get("DEBUG", "False") == "True"
SITE_HOSTNAME = os.environ.get("SITE_HOSTNAME", "localhost")

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
TIMEPERIOD_DAYS_URL_PARAMETER = "days"

FLASK_SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", os.urandom(32))
FLASK_APP_PORT = int(os.environ.get("FLASK_APP_PORT", 3031))

SRI_ATTRIBUTE_VALUES = {
    "bootstrap_js": ("sha256-nXxM3vVk1ByhwczQW2ZCRZedoIL4U5PuQKMoprvQKzE= "
                     "sha384-6yr0NH5/NO/eJn8MXILS94sAfqCcf2wpWTTxRwskNor6dIjwbYjw1/PZpr654rQ5 "
                     "sha512-GTHq28lFyjvEmJ5HcqINJlsDRfYe7v0v6Ru7X8FyOUSngYz+KJs6v3iMiMxGN1z07sbd3zKH0H4WZ3sZMHUPHw=="),
    "price_history_js": ("sha256-RmfvHz3ntUTdzVfX98t2/bErZPvpWxsHoorT8diM4E4= "
                         "sha384-qA1jRP/EfN4JFEUwoZ8c8sBBBqCkDIc9d8vNOU1IL/5340cNGaNUvls8OKRPEanl "
                         "sha512-ndQ99e89Kq8Pot1u98/x1m11+hLHl0fD8WeEnE1lfbjSVlIQ+VRRI+XbUqkV8uaY1/b2fMZtJFDlE5lC1yKbYA=="),
    "search_js": ("sha256-x6jrCBrfzLs34vymj15wO7JYE4dv8+guDsw2gTwLBw4= "
                  "sha384-zMJ85kLYeyaHQm2oOTy8r4EuIf/zjM9KhxZCppMcXBS9m4eXL372gZax+tjMYbhG "
                  "sha512-Z5RQ0pcYZQJlrLNIlEk+0uyUsXLCCOPQj7E6RZRTZGzsguRny81XjfK3PKplLa6Y3yYKFIagzg8j2Ck5HsGehQ=="),
    "status_js": ("sha256-XYZXq+s4OIy2MDUnUh0CyPQo32JaSnRqBjO8S8yjFMI= "
                  "sha384-XZWXnzhX84m11+foEW7WMsw2EE4A9dFc/uXOEnuPt6SgypYJl2Wmv555+5wyM+Sv "
                  "sha512-E/xXX/VCt9W5AqeNz+YQVF2jNVnO7w3A4Fi7l0XHtHo+1GtjZGLNb6Eb+amyCZztKfPhfXpxW7PGBPmjm30MBA=="),
    "book_js": ("sha256-JgxBFm9mLSK3fp3T1m+xKA53BSESdLU539ubqoNU9hM= "
                "sha384-CFgcxa+ns728v2fZ5BuO8tXDFjUOoXrqzFuQj9OTj/l3hfJRZxWtqEEXkGouaqts "
                "sha512-h+NIDb7LNRIEAjRpKewcUzRtuh6HgYb2cZAA82w8py4J8fRG0b18kZqAiElv/o/QGhEJaH28QPOhItyHchn2Bw=="),
    "apexcharts_js": ("sha256-SQkKKOiAPbEWrvIQnoPnAiUIFiQDiTPKu21mYmmY1G8= "
                      "sha384-6foQBJHuUSRZT7FlYD0AkFDsYH7bowmqBulLZUb8S1qBoEItSgOaXiGkxDn9kSLP "
                      "sha512-vIqZt7ReO939RQssENNbZ+Iu3j0CSsgk41nP3AYabLiIFajyebORlk7rKPjGddmO1FQkbuOb2EVK6rJkiHsmag=="),
    "user_js": ("sha256-aKEHc3Kf8tAfE6tLYbIuOlYCT2D/9WTU7um9NJKuMcY= "
                "sha384-ZpmdIt4+irNcJCErXLguTvncm+Y+fbhfwwgYWWfI1b6egMRJwMcl6m2pDVS1Wc67 "
                "sha512-jnl4HxlOclxy2kNihl24xNf2gfVPXRkZIv2NHc380tDtbhGQgFB936VL+HMYtk7K3K7OLjnjNFBkRmcb+JW18w=="),
    "jquery_js": ("sha256-/JqT3SQfawRcv/BIHPThkBvs0OEvtFFmqPF/lYI/Cxo= "
                  "sha384-1H217gwSVyLSIfaLxHbE7dRb3v4mYCKbpQvzx0cegeju1MVsGrX5xXxAvs/HgeFs "
                  "sha512-v2CJ7UaYy4JwqLDIrZUI/4hqeoQieOmAZNXBeQyjo21dadnwR+8ZaIJVT8EE2iyI61OV8e6M8PP2/4hpQINQ/g=="),
    "price_chart_js": ("sha256-nplyvECabg1ucrGD67kLnowW4omKElWJh4XdHmWEThU= "
                       "sha384-wHjoO1W6m3By/6IG0EDWFgSBvAA3bNfM2qZytT83CBoz7o7FtPlFU5VVBFCsrrZD "
                       "sha512-DnLignW8sRBNHfGw7u4jZHvDjewlfa2R0vly+JJWiS0SJxHQVmDd8aEVLc0D3tCvuQJn4oBsfjv7lhDoZ450Ig=="),
}
