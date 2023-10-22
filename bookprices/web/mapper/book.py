import os
from typing import Optional
from flask import url_for
from bookprices.shared.model.book import Book
from bookprices.shared.model.bookstore import BookStoreBookPrice, BookInBookStore
from bookprices.shared.db.book import BookSearchSortOption
from bookprices.web.settings import (
    SEARCH_URL_PARAMETER,
    PAGE_URL_PARAMETER,
    AUTHOR_URL_PARAMETER,
    ORDER_BY_URL_PARAMETER,
    DESCENDING_URL_PARAMETER,
    BOOK_IMAGES_PATH,
    BOOK_FALLBACK_IMAGE_NAME)
from bookprices.web.viewmodels.book import (
    IndexViewModel,
    AuthorOption,
    SortingOption,
    BookListItemViewModel,
    BookPriceForStoreViewModel,
    PriceHistoryViewModel,
    BookDetailsViewModel)


PRICE_NONE_TEXT = "-"
PRICE_CREATED_NONE_TEXT = "Pris ikke hentet"
AUTHOR_DEFAULT_OPTION_TEXT = "Alle forfattere"
INDEX_ENDPOINT = "page.index"
BOOK_ENDPOINT = "page.book"
PRICE_HISTORY_ENDPOINT = "page.price_history"


def _map_sorting_options(search_phrase: str,
                         author: str,
                         order_by: BookSearchSortOption,
                         descending: bool) -> list[SortingOption]:
    sorting_options = [
        SortingOption(
            text="Titel: A til Z",
            selected=order_by == BookSearchSortOption.Title and not descending,
            url=create_url(page_number=1,
                           endpoint="page.index",
                           **{SEARCH_URL_PARAMETER: search_phrase,
                              AUTHOR_URL_PARAMETER: author,
                              ORDER_BY_URL_PARAMETER: BookSearchSortOption.Title.name,
                              DESCENDING_URL_PARAMETER: False})),
        SortingOption(
            text="Titel: Z til A",
            selected=order_by == BookSearchSortOption.Title and descending,
            url=create_url(page_number=1,
                           endpoint="page.index",
                           **{SEARCH_URL_PARAMETER: search_phrase,
                              AUTHOR_URL_PARAMETER: author,
                              ORDER_BY_URL_PARAMETER: BookSearchSortOption.Title.name,
                              DESCENDING_URL_PARAMETER: True})),
        SortingOption(
            text="Forfatter: A til Z",
            selected=order_by == BookSearchSortOption.Author and not descending,
            url=create_url(page_number=1,
                           endpoint="page.index",
                           **{SEARCH_URL_PARAMETER: search_phrase,
                              AUTHOR_URL_PARAMETER: author,
                              ORDER_BY_URL_PARAMETER: BookSearchSortOption.Author.name,
                              DESCENDING_URL_PARAMETER: False})),
        SortingOption(
            text="Forfatter: Z til A",
            selected=order_by == BookSearchSortOption.Author and descending,
            url=create_url(page_number=1,
                           endpoint="page.index",
                           **{SEARCH_URL_PARAMETER: search_phrase,
                              AUTHOR_URL_PARAMETER: author,
                              ORDER_BY_URL_PARAMETER: BookSearchSortOption.Author.name,
                              DESCENDING_URL_PARAMETER: True})),
        SortingOption(
            text="Oprettet: Ældste først",
            selected=order_by == BookSearchSortOption.Created and not descending,
            url=create_url(page_number=1,
                           endpoint="page.index",
                           **{SEARCH_URL_PARAMETER: search_phrase,
                              AUTHOR_URL_PARAMETER: author,
                              ORDER_BY_URL_PARAMETER: BookSearchSortOption.Created.name,
                              DESCENDING_URL_PARAMETER: False})),
        SortingOption(
            text="Oprettet: Nyeste først",
            selected=order_by == BookSearchSortOption.Created and descending,
            url=create_url(page_number=1,
                           endpoint="page.index",
                           **{SEARCH_URL_PARAMETER: search_phrase,
                              AUTHOR_URL_PARAMETER: author,
                              ORDER_BY_URL_PARAMETER: BookSearchSortOption.Created.name,
                              DESCENDING_URL_PARAMETER: True})),
    ]

    return sorting_options


def map_index_vm(books: list[Book],
                 author_names: list[str],
                 search_phrase: str,
                 current_page: int,
                 author: Optional[str],
                 previous_page: Optional[int],
                 next_page: Optional[int],
                 order_by: BookSearchSortOption,
                 descending: bool) -> IndexViewModel:

    author_options = [AuthorOption(AUTHOR_DEFAULT_OPTION_TEXT, "", not author)]
    for author_name in author_names:
        author_options.append(AuthorOption(author_name, author_name, author_name == author))

    sorting_options = _map_sorting_options(search_phrase, author, order_by, descending)
    url_parameters = {
        SEARCH_URL_PARAMETER: search_phrase,
        AUTHOR_URL_PARAMETER: author,
        ORDER_BY_URL_PARAMETER: order_by.name,
        DESCENDING_URL_PARAMETER: descending
    }
    previous_page_url, next_page_url = None, None
    if previous_page:
        previous_page_url = create_url(previous_page,
                                       endpoint=INDEX_ENDPOINT,
                                       **url_parameters)
    if next_page:
        next_page_url = create_url(next_page,
                                   endpoint=INDEX_ENDPOINT,
                                   **url_parameters)

    return IndexViewModel([_map_book_item(b, current_page, url_parameters) for b in books],
                          author_options,
                          sorting_options,
                          search_phrase,
                          author,
                          current_page,
                          previous_page,
                          next_page,
                          previous_page_url,
                          next_page_url)


def _map_book_item(book: Book,
                   page: int,
                   url_parameters: dict) -> BookListItemViewModel:

    image = book.image_url if book.image_url else BOOK_FALLBACK_IMAGE_NAME
    image_url = os.path.join(BOOK_IMAGES_PATH, image)
    url = create_url(page,
                     endpoint=BOOK_ENDPOINT,
                     book_id=book.id,
                     **url_parameters)

    return BookListItemViewModel(book.id, book.isbn, book.title, book.author, url, image_url)


def map_book_details(book: Book,
                     book_prices: list[BookStoreBookPrice],
                     page: Optional[int],
                     author: Optional[str],
                     search_phrase: Optional[str],
                     order_by: BookSearchSortOption,
                     descending: bool) -> BookDetailsViewModel:

    book_price_view_models = []
    for bp in book_prices:
        is_price_available = bp.price is not None
        price_str = bp.price if is_price_available else PRICE_NONE_TEXT
        created_str = bp.created if is_price_available else PRICE_CREATED_NONE_TEXT
        price_history_url = create_url(page,
                                       endpoint=PRICE_HISTORY_ENDPOINT,
                                       book_id=book.id,
                                       store_id=bp.book_store_id,
                                       **{SEARCH_URL_PARAMETER: search_phrase,
                                          AUTHOR_URL_PARAMETER: author,
                                          ORDER_BY_URL_PARAMETER: order_by.name,
                                          DESCENDING_URL_PARAMETER: descending})

        book_price_view_models.append(BookPriceForStoreViewModel(bp.book_store_id,
                                                                 bp.book_store_name,
                                                                 bp.url,
                                                                 price_history_url,
                                                                 price_str,
                                                                 created_str,
                                                                 is_price_available))

    image = book.image_url if book.image_url else BOOK_FALLBACK_IMAGE_NAME
    book.image_url = os.path.join(BOOK_IMAGES_PATH, image)
    index_url = create_url(page,
                           endpoint=INDEX_ENDPOINT,
                           **{SEARCH_URL_PARAMETER: search_phrase,
                              AUTHOR_URL_PARAMETER: author,
                              ORDER_BY_URL_PARAMETER: order_by.name,
                              DESCENDING_URL_PARAMETER: descending})

    author_search_url = create_url(page_number=1,
                                   endpoint=INDEX_ENDPOINT,
                                   **{AUTHOR_URL_PARAMETER: book.author})

    return BookDetailsViewModel(book,
                                book_price_view_models,
                                index_url,
                                author_search_url,
                                page,
                                search_phrase)


def create_url(page_number: int,
               endpoint: str,
               **params) -> str:
    url_params = {name: str(value) for name, value in params.items() if value}
    url_params[PAGE_URL_PARAMETER] = str(page_number)

    return url_for(endpoint, **url_params)


def map_price_history(book_in_book_store: BookInBookStore,
                      page: Optional[int],
                      search_phrase: Optional[str],
                      author: Optional[str],
                      order_by: BookSearchSortOption,
                      descending: bool) -> PriceHistoryViewModel:

    return_url = create_url(page,
                            endpoint=BOOK_ENDPOINT,
                            book_id=book_in_book_store.book.id,
                            **{SEARCH_URL_PARAMETER: search_phrase,
                               AUTHOR_URL_PARAMETER: author,
                               ORDER_BY_URL_PARAMETER: order_by.name,
                               DESCENDING_URL_PARAMETER: descending})

    return PriceHistoryViewModel(book_in_book_store.book,
                                 book_in_book_store.book_store,
                                 book_in_book_store.get_full_url(),
                                 return_url)
