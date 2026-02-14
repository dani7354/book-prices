import os
from datetime import datetime, timedelta, date
from typing import Optional
from flask import url_for
from bookprices.shared.model.book import Book
from bookprices.shared.model.bookstore import BookStoreBookPrice, BookInBookStore, BookStore
from bookprices.shared.db.book import BookSearchSortOption
from bookprices.web.settings import (
    SITE_HOSTNAME,
    SEARCH_URL_PARAMETER,
    PAGE_URL_PARAMETER,
    AUTHOR_URL_PARAMETER,
    ORDER_BY_URL_PARAMETER,
    DESCENDING_URL_PARAMETER,
    BOOK_IMAGES_BASE_URL,
    BOOK_FALLBACK_IMAGE_NAME, BOOKLIST_ID_URL_PARAMETER)
from bookprices.web.shared.enum import Endpoint
from bookprices.web.viewmodels.book import (
    SearchViewModel,
    AuthorOption,
    SortingOption,
    BookListItemViewModel,
    BookPriceForStoreViewModel,
    PriceHistoryViewModel,
    BookDetailsViewModel, BookStoreViewModel, CreateBookViewModel)
from bookprices.web.viewmodels.page import IndexViewModel

DATE_FORMAT = "%d-%m-%Y"

PRICE_NONE_TEXT = "-"
PRICE_UPDATED_YESTERDAY_TEXT = "i går"
PRICE_UPDATED_TODAY_TEXT = "i dag"
PRICE_CREATED_NONE_TEXT = "Pris ikke hentet"
AUTHOR_DEFAULT_OPTION_TEXT = "Alle forfattere"


def _add_ref_to_bookstore_url(url: str) -> str:
    url_stripped = url.rstrip("/")
    return f"{url_stripped}?ref={SITE_HOSTNAME}"


def _get_created_text(created: datetime) -> str:
    today = date.today()
    if created.date() == today:
        return PRICE_UPDATED_TODAY_TEXT
    elif created.date() == today - timedelta(days=1):
        return PRICE_UPDATED_YESTERDAY_TEXT
    else:
        return created.strftime(DATE_FORMAT)


def _create_url(page_number: int,
                endpoint: str,
                **params) -> str:
    url_params = {name: str(value) for name, value in params.items() if value}
    url_params[PAGE_URL_PARAMETER] = str(page_number)

    return url_for(endpoint, **url_params)


def _get_image_url(book: Book) -> str:
    if book.image_url:
        book_image_path = os.path.join(BOOK_IMAGES_BASE_URL, book.image_url)
        return book_image_path
    return str(os.path.join(BOOK_IMAGES_BASE_URL, BOOK_FALLBACK_IMAGE_NAME))


def _was_book_recently_added(book: Book) -> bool:
    return book.created >= datetime.now() - timedelta(days=2)


def _map_sorting_options(search_phrase: str,
                         author: str,
                         order_by: BookSearchSortOption,
                         descending: bool) -> list[SortingOption]:
    sorting_options = [
        SortingOption(
            text="Titel: A til Z",
            selected=order_by == BookSearchSortOption.Title and not descending,
            url=_create_url(page_number=1,
                            endpoint=Endpoint.BOOK_SEARCH.value,
                            **{SEARCH_URL_PARAMETER: search_phrase,
                               AUTHOR_URL_PARAMETER: author,
                               ORDER_BY_URL_PARAMETER: BookSearchSortOption.Title.name,
                               DESCENDING_URL_PARAMETER: False})),
        SortingOption(
            text="Titel: Z til A",
            selected=order_by == BookSearchSortOption.Title and descending,
            url=_create_url(page_number=1,
                            endpoint=Endpoint.BOOK_SEARCH.value,
                            **{SEARCH_URL_PARAMETER: search_phrase,
                               AUTHOR_URL_PARAMETER: author,
                               ORDER_BY_URL_PARAMETER: BookSearchSortOption.Title.name,
                               DESCENDING_URL_PARAMETER: True})),
        SortingOption(
            text="Forfatter: A til Z",
            selected=order_by == BookSearchSortOption.Author and not descending,
            url=_create_url(page_number=1,
                            endpoint=Endpoint.BOOK_SEARCH.value,
                            **{SEARCH_URL_PARAMETER: search_phrase,
                               AUTHOR_URL_PARAMETER: author,
                               ORDER_BY_URL_PARAMETER: BookSearchSortOption.Author.name,
                               DESCENDING_URL_PARAMETER: False})),
        SortingOption(
            text="Forfatter: Z til A",
            selected=order_by == BookSearchSortOption.Author and descending,
            url=_create_url(page_number=1,
                            endpoint=Endpoint.BOOK_SEARCH.value,
                            **{SEARCH_URL_PARAMETER: search_phrase,
                               AUTHOR_URL_PARAMETER: author,
                               ORDER_BY_URL_PARAMETER: BookSearchSortOption.Author.name,
                               DESCENDING_URL_PARAMETER: True})),
        SortingOption(
            text="Ældste først",
            selected=order_by == BookSearchSortOption.Created and not descending,
            url=_create_url(page_number=1,
                            endpoint=Endpoint.BOOK_SEARCH.value,
                            **{SEARCH_URL_PARAMETER: search_phrase,
                               AUTHOR_URL_PARAMETER: author,
                               ORDER_BY_URL_PARAMETER: BookSearchSortOption.Created.name,
                               DESCENDING_URL_PARAMETER: False})),
        SortingOption(
            text="Nyeste først",
            selected=order_by == BookSearchSortOption.Created and descending,
            url=_create_url(page_number=1,
                            endpoint=Endpoint.BOOK_SEARCH.value,
                            **{SEARCH_URL_PARAMETER: search_phrase,
                               AUTHOR_URL_PARAMETER: author,
                               ORDER_BY_URL_PARAMETER: BookSearchSortOption.Created.name,
                               DESCENDING_URL_PARAMETER: True})),
        SortingOption(
            text="Seneste priser",
            selected=order_by == BookSearchSortOption.PriceUpdated,
            url=_create_url(page_number=1,
                            endpoint=Endpoint.BOOK_SEARCH.value,
                            **{SEARCH_URL_PARAMETER: search_phrase,
                               AUTHOR_URL_PARAMETER: author,
                               ORDER_BY_URL_PARAMETER: BookSearchSortOption.PriceUpdated.name,
                               DESCENDING_URL_PARAMETER: True})),
    ]

    return sorting_options


def map_index_vm(
        newest_books: list[Book],
        latest_updated_books: list[Book],
        book_ids_from_booklist: set[int],
        booklist_active: bool) -> IndexViewModel:
    url_parameters_newest_books = {
        ORDER_BY_URL_PARAMETER: BookSearchSortOption.Created.name,
        DESCENDING_URL_PARAMETER: True,
    }
    newest_books_url = _create_url(
        page_number=1,
        endpoint=Endpoint.BOOK_SEARCH.value,
        **url_parameters_newest_books)

    url_parameters_latest_prices = {
        ORDER_BY_URL_PARAMETER: BookSearchSortOption.PriceUpdated.name,
        DESCENDING_URL_PARAMETER: True,
    }
    latest_prices_url = _create_url(
        page_number=1,
        endpoint=Endpoint.BOOK_SEARCH.value,
        **url_parameters_latest_prices)

    newest_books_models = [
        map_book_item(
            book=b,
            page=1,
            url_parameters=url_parameters_newest_books,
            on_current_booklist=booklist_active and b.id in book_ids_from_booklist) for b in newest_books]

    latest_updated_books_models = [
        map_book_item(
            book=b,
            page=1,
            url_parameters=url_parameters_latest_prices,
            on_current_booklist=booklist_active and b.id in book_ids_from_booklist) for b in latest_updated_books]

    return IndexViewModel(
        newest_books=newest_books_models,
        latest_prices_books=latest_updated_books_models,
        newest_books_url=newest_books_url,
        latest_prices_books_url=latest_prices_url,
        booklist_active=booklist_active)


def map_search_vm(books: list[Book],
                  author_names: list[str],
                  book_ids_from_booklist: set[int],
                  search_phrase: str,
                  current_page: int,
                  author: Optional[str],
                  previous_page: Optional[int],
                  next_page: Optional[int],
                  order_by: BookSearchSortOption,
                  descending: bool,
                  booklist_active: bool) -> SearchViewModel:

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
        previous_page_url = _create_url(previous_page,
                                        endpoint=Endpoint.BOOK_SEARCH.value,
                                        **url_parameters)
    if next_page:
        next_page_url = _create_url(next_page,
                                    endpoint=Endpoint.BOOK_SEARCH.value,
                                    **url_parameters)

    book_models = [
        map_book_item(
            book=b,
            page=current_page,
            url_parameters=url_parameters,
            on_current_booklist=book_ids_from_booklist and b.id in book_ids_from_booklist)
        for b in books]

    return SearchViewModel(book_models,
                           author_options,
                           sorting_options,
                           search_phrase,
                           author,
                           current_page,
                           previous_page,
                           next_page,
                           previous_page_url,
                           next_page_url,
                           booklist_active)


def map_book_item(book: Book,
                  page: int,
                  url_parameters: dict,
                  on_current_booklist: bool) -> BookListItemViewModel:

    image_url = _get_image_url(book)
    was_added_recently = _was_book_recently_added(book)
    url = _create_url(page,
                      endpoint=Endpoint.BOOK.value,
                      book_id=book.id,
                      **url_parameters)

    return BookListItemViewModel(
        book.id, book.isbn, book.title, book.author, url, image_url, was_added_recently, on_current_booklist)


def _create_return_url_for_book_details(
        endpoint: Endpoint,
        page: int | None,
        booklist_id: int | None,
        search_phrase: str | None,
        author: str | None,
        return_endpoint: Endpoint,
        order_by: BookSearchSortOption,
        descending: bool) -> str:

    if endpoint == Endpoint.BOOK_SEARCH:
        return_url = _create_url(page,
                           endpoint=return_endpoint.value,
                           **{SEARCH_URL_PARAMETER: search_phrase,
                              AUTHOR_URL_PARAMETER: author,
                              ORDER_BY_URL_PARAMETER: order_by.name,
                              DESCENDING_URL_PARAMETER: descending})
    elif endpoint == Endpoint.BOOKLIST_VIEW:
        return_url = _create_url(page,
                           endpoint=return_endpoint.value,
                           **{BOOKLIST_ID_URL_PARAMETER: booklist_id})
    else:
        return_url = url_for(Endpoint.PAGE_INDEX.value)

    return return_url

def map_book_details(book: Book,
                     book_prices: list[BookStoreBookPrice],
                     user_can_edit_and_delete: bool,
                     page: int | None,
                     booklist_id: int | None,
                     author: str | None,
                     search_phrase: str | None,
                     return_endpoint: Endpoint,
                     order_by: BookSearchSortOption,
                     descending: bool,
                     booklist_active: bool,
                     on_current_booklist: bool) -> BookDetailsViewModel:

    book_price_view_models = []
    for bp in book_prices:
        is_price_available = bp.price is not None
        price_str = bp.price if is_price_available else PRICE_NONE_TEXT
        created_str = _get_created_text(bp.created) if is_price_available else PRICE_CREATED_NONE_TEXT
        url_with_ref = _add_ref_to_bookstore_url(bp.url)
        price_history_url = _create_url(page,
                                        endpoint=Endpoint.BOOK_PRICE_HISTORY.value,
                                        book_id=book.id,
                                        store_id=bp.book_store_id,
                                        **{SEARCH_URL_PARAMETER: search_phrase,
                                           AUTHOR_URL_PARAMETER: author,
                                           ORDER_BY_URL_PARAMETER: order_by.name,
                                           DESCENDING_URL_PARAMETER: descending})

        book_price_view_models.append(
            BookPriceForStoreViewModel(
                bp.book_store_id,
                bp.book_store_name,
                url_with_ref,
                price_history_url,
                price_str,
                created_str,
                is_price_available))

    image = book.image_url if book.image_url else BOOK_FALLBACK_IMAGE_NAME
    image_url = os.path.join(BOOK_IMAGES_BASE_URL, image)
    created_formated = book.created.strftime(DATE_FORMAT)

    return_url = _create_return_url_for_book_details(
        endpoint=return_endpoint,
        page=page,
        booklist_id=booklist_id,
        search_phrase=search_phrase,
        author=author,
        return_endpoint=return_endpoint,
        order_by=order_by,
        descending=descending)

    author_search_url = _create_url(page_number=1,
                                    endpoint=Endpoint.BOOK_SEARCH.value,
                                    **{AUTHOR_URL_PARAMETER: book.author})

    return BookDetailsViewModel(
        id=book.id,
        title=book.title,
        author=book.author,
        isbn=book.isbn,
        format=book.format,
        created=created_formated,
        image_url=image_url,
        book_prices=book_price_view_models,
        return_url=return_url,
        author_search_url=author_search_url,
        page=page,
        search_phrase=search_phrase,
        show_edit_and_delete_buttons=user_can_edit_and_delete,
        book_on_current_booklist=booklist_active and on_current_booklist)


def map_price_history(book_in_book_store: BookInBookStore,
                      page: Optional[int],
                      search_phrase: Optional[str],
                      author: Optional[str],
                      order_by: BookSearchSortOption,
                      descending: bool) -> PriceHistoryViewModel:

    return_url = _create_url(page,
                             endpoint=Endpoint.BOOK.value,
                             book_id=book_in_book_store.book.id,
                             **{SEARCH_URL_PARAMETER: search_phrase,
                                AUTHOR_URL_PARAMETER: author,
                                ORDER_BY_URL_PARAMETER: order_by.name,
                                DESCENDING_URL_PARAMETER: descending})

    return PriceHistoryViewModel(book_in_book_store.book,
                                 book_in_book_store.book_store,
                                 _add_ref_to_bookstore_url(book_in_book_store.get_full_url()),
                                 return_url)


def map_bookstores(bookstores: list[BookStore]) -> list[BookStoreViewModel]:
    return [BookStoreViewModel(bs.name, f"{bs.url}?ref={SITE_HOSTNAME}") for bs in bookstores]


def map_to_create_view_model(
        book: Book,
        form_action_url: str,
        available_book_images: list[str]) -> CreateBookViewModel:
    return CreateBookViewModel(
        id=book.id,
        isbn=book.isbn,
        title=book.title,
        author=book.author,
        format=book.format,
        image_url=book.image_url,
        form_action_url=form_action_url,
        image_base_url=BOOK_IMAGES_BASE_URL,
        available_images=available_book_images)


def map_from_create_view_model(view_model: CreateBookViewModel) -> Book:
    return Book(
        id=view_model.id,
        title=view_model.title,
        author=view_model.author,
        format=view_model.format,
        isbn=view_model.isbn,
        image_url=view_model.image_url)
