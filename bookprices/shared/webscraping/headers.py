BASE_HEADERS = {
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,image/apng,*/*;q=0.8,"
        "application/signed-exchange;v=b3;q=0.7"
    ),
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Sec-GPC": "1",
    "Sec-CH-UA": '"Chromium";v="151", "Not=A?Brand";v="99"',
    "Sec-CH-UA-Mobile": "?0",
    "Sec-CH-UA-Model": '""',
    "Sec-CH-UA-Platform": '"Linux"',
    "Sec-CH-UA-Platform-Version": '""',
    "Sec-CH-UA-Arch": '"x86"',
    "Sec-CH-UA-Bitness": '"64"',
    "Sec-CH-UA-Full-Version": '"151.0.7922.137"',
    "Upgrade-Insecure-Requests": "1",
    "Pragma": "no-cache",
}

HTTP_HEADERS_FOR_SAXO = {
    **BASE_HEADERS,
    "Referer": "https://www.saxo.com",
}

HTTP_HEADERS_FOR_BOGIDE = {
    **BASE_HEADERS,
    "Cookie": "localization=DK; cart_currency=DKK;",
    "DNT": "1",
    "Referer": "https://www.bogide.dk/",
}

HTTP_HEADERS_FOR_ACADEMIC_BOOKS = {
    **BASE_HEADERS,
    "Cache-Control": "no-cache",
    "DNT": "1",
    "Referer": "https://www.academicbooks.dk/",
}

HTTP_HEADERS_FOR_WILLIAMDAM = {
    **BASE_HEADERS,
    "Cache-Control": "no-cache",
    "DNT": "1",
    "Referer": "https://www.williamdam.dk/",
}

HTTP_HEADERS_FOR_IMUSIC = {
    **BASE_HEADERS,
    "Cache-Control": "no-cache",
    "DNT": "1",
    "Referer": "https://imusic.dk?query=",
    "Host": "imusic.dk",
}
