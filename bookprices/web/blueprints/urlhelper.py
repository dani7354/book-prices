from urllib3.util import parse_url, Url
from werkzeug.datastructures.structures import MultiDict
from bookprices.shared.db.book import BookSearchSortOption
from bookprices.web.settings import (
    SEARCH_URL_PARAMETER,
    AUTHOR_URL_PARAMETER,
    PAGE_URL_PARAMETER,
    ORDER_BY_URL_PARAMETER,
    DESCENDING_URL_PARAMETER)


def parse_args_for_search(request_args: MultiDict) -> dict:
    args = {
        SEARCH_URL_PARAMETER: request_args.get(SEARCH_URL_PARAMETER, type=str, default=""),
        AUTHOR_URL_PARAMETER: request_args.get(AUTHOR_URL_PARAMETER, type=str, default=""),
        DESCENDING_URL_PARAMETER: request_args.get(DESCENDING_URL_PARAMETER, type=bool, default=False)
    }

    order_by = request_args.get(ORDER_BY_URL_PARAMETER, type=str)
    if sort_option := BookSearchSortOption.from_str(order_by):
        args[ORDER_BY_URL_PARAMETER] = sort_option
    else:
        args[ORDER_BY_URL_PARAMETER] = BookSearchSortOption.Title

    if (page := request_args.get(PAGE_URL_PARAMETER, type=int, default=1)) and page > 0:
        args[PAGE_URL_PARAMETER] = page
    else:
        args[PAGE_URL_PARAMETER] = 1

    return args


def format_url_for_redirection(url: str) -> str:
    parsed_url = parse_url(url)
    
    return Url(path=parsed_url.path, query=parsed_url.query).url
