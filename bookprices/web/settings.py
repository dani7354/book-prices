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
JOB_API_CLIENT_ID = "JobApiWeb"

# App settings
DEBUG_MODE = os.environ.get("DEBUG", "False") == "True"
SITE_HOSTNAME = os.environ.get("SITE_HOSTNAME", "localhost")

BOOK_PAGESIZE = 20
BOOK_IMAGES_BASE_URL = "/static/assets/images/books/" if DEBUG_MODE else "/static/images/books/"
BOOK_FALLBACK_IMAGE_NAME = "default.png"
BOOK_IMAGE_FILE_PATH = os.environ["BOOK_IMAGE_FILE_PATH"]

AUTHOR_URL_PARAMETER = "author"
SEARCH_URL_PARAMETER = "search"
ORDER_BY_URL_PARAMETER = "orderby"
PAGE_URL_PARAMETER = "page"
DESCENDING_URL_PARAMETER = "descending"
GOOGLE_AUTH_ERROR_URL_PARAMETER = "error"
GOOGLE_AUTH_CODE_URL_PARAMETER = "code"
TIMEPERIOD_DAYS_URL_PARAMETER = "days"
BOOKLIST_ID_URL_PARAMETER = "booklist_id"

FLASK_SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", os.urandom(32))
FLASK_APP_PORT = int(os.environ.get("FLASK_APP_PORT", 3031))

SRI_ATTRIBUTE_VALUES = {
    "bootstrap_js": ("sha256-mkoRoV24jV+rCPWcHDR5awPx8VuzzJKN0ibhxZ9/WaM= "
                     "sha384-5xO2n1cyGKAe630nacBqFQxWoXjUIkhoc/FxQrWM07EIZ3TuqkAsusDeyPDOIeid "
                     "sha512-sSOeacod972lTNk0ePyxrSSI6yoqvGRm7bbqtwqsY1r7TcdYiQn/a+KvaYQ0iacHBYE/MSEVjTNa2dglSz74vA=="),
    "price_history_js": ("sha256-5TeNiYelgBCwoDItZTmYwbScsVDMk+YXTe4Cmllx0M8= "
                         "sha384-oftkcSTZH+qftcBGq5HPzAf4N7v/Smknu8XneO8BJalbmvEKDny6E6qn84xjRaCr "
                         "sha512-lJSauAtO5SK1S90/mCTy706X8FHX1bNlyzOKfxOr8mLZJWuRKXvfNJj3Q7ohO2sAdS5JwYDm3VQcuuGhFH5Vzg=="),
    "search_js": ("sha256-x6jrCBrfzLs34vymj15wO7JYE4dv8+guDsw2gTwLBw4= "
                  "sha384-zMJ85kLYeyaHQm2oOTy8r4EuIf/zjM9KhxZCppMcXBS9m4eXL372gZax+tjMYbhG "
                  "sha512-Z5RQ0pcYZQJlrLNIlEk+0uyUsXLCCOPQj7E6RZRTZGzsguRny81XjfK3PKplLa6Y3yYKFIagzg8j2Ck5HsGehQ=="),
    "status_js": ("sha256-XYZXq+s4OIy2MDUnUh0CyPQo32JaSnRqBjO8S8yjFMI= "
                  "sha384-XZWXnzhX84m11+foEW7WMsw2EE4A9dFc/uXOEnuPt6SgypYJl2Wmv555+5wyM+Sv "
                  "sha512-E/xXX/VCt9W5AqeNz+YQVF2jNVnO7w3A4Fi7l0XHtHo+1GtjZGLNb6Eb+amyCZztKfPhfXpxW7PGBPmjm30MBA=="),
    "book_js": ("sha256-ksumcu4R2xURc6vKSeMzzP9YTz3y2lVvhTzUoKzM9+Y= "
                "sha384-HyrFTCYmUdoLpv+cbiY1xutb3nWahLHn4QQZBq9EBpjGtYhbBMZrso3hsVfeN3Ln "
                "sha512-+UjqPHpLx52FfgXAWO6sc70sn/MJ/MwgvO854kVyx2P4wG0zDwIwiAJaLeyxCUw74xQz4iI8Fl2O6M/gtw9aBg=="),
    "delete_book_js": ("sha256-AIfsCGXJzClcfQzpYC/Lr9qjsmvx48b3CQgZkDN29VU= "
                       "sha384-xmaDaVKu+2JW3BW7+E5CQao565H1LcFVaksrPQiFDOiXh26MRkSvT3OEMADmcIDU "
                       "sha512-Shy8W4MwvOvGAU84JxASTUynjvw15jIQgPSVD0ydCiG6T9uPap5Ohtnn4RUe65dmDHBLCpKuFzAAXJuTpaAo/Q=="),
    "edit_book_js": ("sha256-jMZ9rYmqFeNXDIO3IofnMmq8jx0wlqif1l6FwHJfT0Y= "
                     "sha384-a1D9decWOBd2taUpa4o0X1pTkjDIO8houWhltI/CKds5dOZv+0zQ+pKuxzvmD57d "
                     "sha512-l3MTEvUs1vKHQ8NVWaZhUZaugmWx/+IFaPvxdFuUvNdhy0VLJLBuAltHehLaXuKMH210AxgnfEwGpm9De7D17A=="),
    "delete_bookstore_js": ("sha256-UBp9FUrAeNswGmwyYKD8JHtYZe1ulsGo/p3/KvBH4Kk= "
                            "sha384-9+n38rM7E7qdsioE26Ps6U6hEYoq/ma9Drl1btzml/8TT8ir/7Z4B0TLW8/pJ2B0 "
                            "sha512-fdZ7NzvosQvDlVYNxkGHP/gC5FK6RW0MnzQq7ZB8EKMqy1QQ0Ip/8e6TfwC+dy+8lgVzhkONUM7C9Uo2Bn4Cdw=="),
    "apexcharts_js": ("sha256-VvsSKf53yMxm8x6hJb6p7TejhAyXtmoj5EyFHP9xeys= "
                      "sha384-KNaFJ+EK516RuHsoycvreec5pD7BkTKJEkjMrVSQWu9KGTl7En4dhIDv7t1DFJ+g "
                      "sha512-yR5RFcmaHqsGbB9WPG104Fk3+x2s9fMYCgA09VaRT2Lqpay6oNhKldYsZKU/rpYqbsNVhN5+RTbQBSd9+DhL6g=="),
    "user_js": ("sha256-aKEHc3Kf8tAfE6tLYbIuOlYCT2D/9WTU7um9NJKuMcY= "
                "sha384-ZpmdIt4+irNcJCErXLguTvncm+Y+fbhfwwgYWWfI1b6egMRJwMcl6m2pDVS1Wc67 "
                "sha512-jnl4HxlOclxy2kNihl24xNf2gfVPXRkZIv2NHc380tDtbhGQgFB936VL+HMYtk7K3K7OLjnjNFBkRmcb+JW18w=="),
    "delete_user_js": ("sha256-KPXwacPFr76zwXqi3KH/0tpXOFkqDE9Ap84NmYUipAc= "
                       "sha384-+VL1JPQ60RG49J1TkyLOnvPhJsWkq3PIbvjZpggvFSkcaFTjsvuINnf5Q98+pY/+ "
                       "sha512-heleqxRjTHQAl+70CReT8/3u/xiwzoWFqhl51d7X/HMXF+FVFbpNFTgB1+r1ZgLJxmbLR3m+UlbJ01qXvE0U2g=="),
    "jquery_js": ("sha256-/JqT3SQfawRcv/BIHPThkBvs0OEvtFFmqPF/lYI/Cxo= "
                  "sha384-1H217gwSVyLSIfaLxHbE7dRb3v4mYCKbpQvzx0cegeju1MVsGrX5xXxAvs/HgeFs "
                  "sha512-v2CJ7UaYy4JwqLDIrZUI/4hqeoQieOmAZNXBeQyjo21dadnwR+8ZaIJVT8EE2iyI61OV8e6M8PP2/4hpQINQ/g=="),
    "price_chart_js": ("sha256-0MC9H+BsSSWDojqimteKzhMIu95VrGRXAdAhtR3DY6I= "
                       "sha384-q/mJ3N23EEUdKg+IAACohdR2WgzlFQv8YlyOS7X3Mb87zjKF8F71Gq9kcE3S+qIp "
                       "sha512-/vXxBZIcj4xdIEmaMGNOudnLr4DNsDO0lJdgi/ZPQNIABX3QQtlzJzA9DCZxyDNLpjru+KpX/2Vh3njdcf4MZQ=="),
    "job_js": ("sha256-rWaJ0ejh0Bf9ppZlXxhFqxF6sQ3c0NUQFswEfkGCdO4= "
               "sha384-1UmwrFcVNAAqsH5t7OE+q0ouA+fCHNK2ee57Ts6CuNyA6zBktZG9WsyuTpmS3NCJ "
               "sha512-VV0Nec3Q4VRwJ6epRhp+ci/2U1gJ8w8Hdoxx36xSgJUE3MO688a2wki633CdF6hfSInnGs11XcDBUp48vKWlnw=="),
    "job_run_js": ("sha256-dzHGVg7PDzfXt3E5CbkEoBKonNm138IQzQG7CNbBWXE= "
                   "sha384-U8UteYjyRxY1qQpBKnQyP7XsPHaREbD9LD1qPlMnMjUKifYtXQwUsPrldTY7UF8l "
                   "sha512-JjWA5y98IUQjyPbryCz7oEBv+lYCMcjoVJPnG4o1fsRYb9CO2ppGWnSaCnmmjXP//yS0XqO2aF8Eqby4BE9oYA=="),
    "job_common_js": ("sha256-gYkCb1U4rklPflQzazqBxREfHORqt3a6qjlFncweHmc= "
                      "sha384-edtar1CZDwvBCghJzixGSJGe9PTJRkOFqnMvdMbf/bquB+O9krn1g0w4CsmOzrsU "
                      "sha512-fSSNYDVZzXIP/pSzGRxeXAgDwQttx/SzPmHFgQ2C9yOXuBYjDeP8Vg8Ku6Wbo0IcugBDOO+0qZ6FLlTFoZDvwQ=="),
    "job_run_modal_js": ("sha256-mWSWhUYXMU8ml3ueC2EDBABRLTHOeBXKa57GCEtFxB4= "
                         "sha384-e96AaRmLQhoFTx4SewulM+/l2rqlFU1Mh/vfDMeM5rWXW7Ig59PVOMSQFmAMmQTm "
                         "sha512-TXmOaHNuWUPoyD5oDfVYdHbzhyPg9CsFdF24WubycLTGQqSV+31LD9GXk9AijUfbZnUQRVc+gAqkT0AmhH96VA=="),
}
