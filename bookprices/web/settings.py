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

# Job API settings
JOB_API_BASE_URL = os.environ["JOB_API_BASE_URL"]
JOB_API_USERNAME = os.environ["JOB_API_USERNAME"]
JOB_API_PASSWORD = os.environ["JOB_API_PASSWORD"]

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
    "bootstrap_js": ("sha256-mkoRoV24jV+rCPWcHDR5awPx8VuzzJKN0ibhxZ9/WaM= "
                     "sha384-5xO2n1cyGKAe630nacBqFQxWoXjUIkhoc/FxQrWM07EIZ3TuqkAsusDeyPDOIeid "
                     "sha512-sSOeacod972lTNk0ePyxrSSI6yoqvGRm7bbqtwqsY1r7TcdYiQn/a+KvaYQ0iacHBYE/MSEVjTNa2dglSz74vA=="),
    "price_history_js": ("sha256-shmTHJ9BtJfMMKSojxCajTFs/toh6W/KYr2viwz7sEU= "
                         "sha384-B6B3ip4QGI0AfD/fYaOJVvMEjZ+IohOe3poOoqTJra07+80LMCiQZTufnDzsqCLG "
                         "sha512-XHjEbzJW5ARlIZjNYO5Mn5tN4i402FElt4SQelsZWb/NZY2jr71ZkIY21nUfAC8T6xO6dwBsegfahINSWNjsbA=="),
    "search_js": ("sha256-x6jrCBrfzLs34vymj15wO7JYE4dv8+guDsw2gTwLBw4= "
                  "sha384-zMJ85kLYeyaHQm2oOTy8r4EuIf/zjM9KhxZCppMcXBS9m4eXL372gZax+tjMYbhG "
                  "sha512-Z5RQ0pcYZQJlrLNIlEk+0uyUsXLCCOPQj7E6RZRTZGzsguRny81XjfK3PKplLa6Y3yYKFIagzg8j2Ck5HsGehQ=="),
    "status_js": ("sha256-XYZXq+s4OIy2MDUnUh0CyPQo32JaSnRqBjO8S8yjFMI= "
                  "sha384-XZWXnzhX84m11+foEW7WMsw2EE4A9dFc/uXOEnuPt6SgypYJl2Wmv555+5wyM+Sv "
                  "sha512-E/xXX/VCt9W5AqeNz+YQVF2jNVnO7w3A4Fi7l0XHtHo+1GtjZGLNb6Eb+amyCZztKfPhfXpxW7PGBPmjm30MBA=="),
    "book_js": ("sha256-JgxBFm9mLSK3fp3T1m+xKA53BSESdLU539ubqoNU9hM= "
                "sha384-CFgcxa+ns728v2fZ5BuO8tXDFjUOoXrqzFuQj9OTj/l3hfJRZxWtqEEXkGouaqts "
                "sha512-h+NIDb7LNRIEAjRpKewcUzRtuh6HgYb2cZAA82w8py4J8fRG0b18kZqAiElv/o/QGhEJaH28QPOhItyHchn2Bw=="),
    "apexcharts_js": ("sha256-VvsSKf53yMxm8x6hJb6p7TejhAyXtmoj5EyFHP9xeys= "
                      "sha384-KNaFJ+EK516RuHsoycvreec5pD7BkTKJEkjMrVSQWu9KGTl7En4dhIDv7t1DFJ+g "
                      "sha512-yR5RFcmaHqsGbB9WPG104Fk3+x2s9fMYCgA09VaRT2Lqpay6oNhKldYsZKU/rpYqbsNVhN5+RTbQBSd9+DhL6g=="),
    "user_js": ("sha256-aKEHc3Kf8tAfE6tLYbIuOlYCT2D/9WTU7um9NJKuMcY= "
                "sha384-ZpmdIt4+irNcJCErXLguTvncm+Y+fbhfwwgYWWfI1b6egMRJwMcl6m2pDVS1Wc67 "
                "sha512-jnl4HxlOclxy2kNihl24xNf2gfVPXRkZIv2NHc380tDtbhGQgFB936VL+HMYtk7K3K7OLjnjNFBkRmcb+JW18w=="),
    "jquery_js": ("sha256-/JqT3SQfawRcv/BIHPThkBvs0OEvtFFmqPF/lYI/Cxo= "
                  "sha384-1H217gwSVyLSIfaLxHbE7dRb3v4mYCKbpQvzx0cegeju1MVsGrX5xXxAvs/HgeFs "
                  "sha512-v2CJ7UaYy4JwqLDIrZUI/4hqeoQieOmAZNXBeQyjo21dadnwR+8ZaIJVT8EE2iyI61OV8e6M8PP2/4hpQINQ/g=="),
    "price_chart_js": ("sha256-nplyvECabg1ucrGD67kLnowW4omKElWJh4XdHmWEThU= "
                       "sha384-wHjoO1W6m3By/6IG0EDWFgSBvAA3bNfM2qZytT83CBoz7o7FtPlFU5VVBFCsrrZD "
                       "sha512-DnLignW8sRBNHfGw7u4jZHvDjewlfa2R0vly+JJWiS0SJxHQVmDd8aEVLc0D3tCvuQJn4oBsfjv7lhDoZ450Ig=="),
    "job_js": ("sha256-oNMlSnpnF6VvB4LeWrC0jqZzpzqsJWx4+Abkyh32PI0= "
               "sha384-A0/HOGoDL/AQpnbJC+lSYvHTgdotPlix7gcrk94fESCRPAaFa5JwvLkSXXEBXn6G "
               "sha512-ntAbJQLlqaQ4Lm/OHfulgg2kcc5gz17SA1DFQsLor2lkKxwTjQVP09miUnBBxMe26bowkb35REdiyJFRfma+cA=="),
    "job_run_js": ("sha256-dzHGVg7PDzfXt3E5CbkEoBKonNm138IQzQG7CNbBWXE= "
                   "sha384-U8UteYjyRxY1qQpBKnQyP7XsPHaREbD9LD1qPlMnMjUKifYtXQwUsPrldTY7UF8l "
                   "sha512-JjWA5y98IUQjyPbryCz7oEBv+lYCMcjoVJPnG4o1fsRYb9CO2ppGWnSaCnmmjXP//yS0XqO2aF8Eqby4BE9oYA=="),
    "job_common_js": ("sha256-fZP402wLh5rrHqIVxnlEZKzwe+u9ADZKnbkaSqJ6hFE= "
                      "sha384-F/RqKp2/axGZI2fJJ/oCiN2BBXBAH+G3QE2+o4kN7i9OnycQw0k9SLYc62AUsJ6s "
                      "sha512-7MRvCKF0JDfcu0RHyUiPjgBRoXgTNdrI+m8mJqfySEcFtsbcOY8dxoC1qFXQZZM4AD/S4J5KB6HRU5gLzr2zSA=="),
    "job_run_modal_js": ("sha256-CS0I/HNxfkMNLVogi89EIj/FYHzAvXCWJA1aap/FQOc= "
                         "sha384-00CqRQwYUDPp/T/cC11KJ0dNtMFR7a/GOUe1DQB7+pb72rKLmLsvfclzAPVwjDNc "
                         "sha512-FdaUmNyL6Vgb7dJlD8Q5JuLyiVdz6I22zRhyhoNixHxElFuUqB1WMDC4zEPwud9XdlrArCR2BXJ6TXInMi9Ldg=="),
}
