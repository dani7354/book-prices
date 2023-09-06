import os
from typing import Optional
from flask import url_for
from bookprices.web.viewmodels.book import (IndexViewModel, AuthorOption, BookListItemViewModel,
                                            BookPriceForStoreViewModel, PriceHistoryViewModel, BookDetailsViewModel)
from bookprices.shared.model.book import Book
from bookprices.shared.model.bookprice import BookPrice
from bookprices.shared.model.bookstore import BookStoreBookPrice, BookInBookStore

PRICE_NONE_TEXT = "-"
PRICE_CREATED_NONE_TEXT = "Pris ikke hentet"
AUTHOR_DEFAULT_OPTION_TEXT = "Alle forfattere"


def map_index_vm(books: list[Book],
                 author_names: list[str],
                 search_phrase: str,
                 image_base_url: str,
                 fallback_image: str,
                 current_page: int,
                 author: Optional[str],
                 previous_page: Optional[int],
                 next_page: Optional[int]) -> IndexViewModel:

    author_options = [AuthorOption(AUTHOR_DEFAULT_OPTION_TEXT, "", not author)]
    for author_name in author_names:
        author_options.append(AuthorOption(author_name, author_name, author_name == author))

    previous_page_url = None
    next_page_url = None
    if previous_page:
        previous_page_url = create_url(previous_page, "index", search=search_phrase, author=author)
    if next_page:
        next_page_url = create_url(next_page, "index", search=search_phrase, author=author)

    return IndexViewModel([map_book_list_item(b, image_base_url, fallback_image, search_phrase, author, current_page) for b in books],
                          author_options,
                          search_phrase,
                          author,
                          current_page,
                          previous_page,
                          next_page,
                          previous_page_url,
                          next_page_url)


def map_book_list_item(book: Book,
                       image_base_url: str,
                       fallback_image: str,
                       search_phrase: Optional[str],
                       author: Optional[str],
                       page: int) -> BookListItemViewModel:

    if book.image_url is not None:
        image_url = os.path.join(image_base_url, book.image_url)
    else:
        image_url = os.path.join(image_base_url, fallback_image)

    url = create_url(page, "book", book_id=book.id, search=search_phrase, author=author)

    return BookListItemViewModel(book.id, book.isbn, book.title, book.author, url, image_url)


def map_book_details(book: Book,
                     book_prices: list[BookStoreBookPrice],
                     image_base_url: str,
                     fallback_image: str,
                     plot_data: str,
                     page: Optional[int],
                     author: Optional[str],
                     search_phrase: Optional[str]) -> BookDetailsViewModel:

    book_price_view_models = []
    for bp in book_prices:
        is_price_available = bp.price is not None
        price_str = bp.price if is_price_available else PRICE_NONE_TEXT
        created_str = bp.created if is_price_available else PRICE_CREATED_NONE_TEXT
        price_history_url = create_url(page,
                                       endpoint="price_history",
                                       book_id=book.id,
                                       store_id=bp.book_store_id,
                                       search=search_phrase,
                                       author=author)

        book_price_view_models.append(BookPriceForStoreViewModel(bp.book_store_id,
                                                                 bp.book_store_name,
                                                                 bp.url,
                                                                 price_history_url,
                                                                 price_str,
                                                                 created_str,
                                                                 is_price_available))

    if book.image_url is not None:
        book.image_url = os.path.join(image_base_url, book.image_url)
    else:
        book.image_url = os.path.join(image_base_url, fallback_image)

    index_url = create_url(page, endpoint="index", search=search_phrase, author=author)

    return BookDetailsViewModel(book,
                                book_price_view_models,
                                plot_data,
                                index_url,
                                page,
                                search_phrase)


def create_url(page_number: int,
               endpoint: str,
               **params) -> str:
    url_params = {name: str(value) for name, value in params.items() if value}
    url_params["page"] = str(page_number)

    return url_for(endpoint, **url_params)


def map_price_history(book_in_book_store: BookInBookStore,
                      book_prices: list[BookPrice],
                      plot_base64: str,
                      page: Optional[int],
                      search_phrase: Optional[str],
                      author: Optional[str]) -> PriceHistoryViewModel:

    return_url = create_url(page,
                            endpoint="book",
                            book_id=book_in_book_store.book.id,
                            search=search_phrase,
                            author=author)

    return PriceHistoryViewModel(book_in_book_store.book,
                                 book_in_book_store.book_store,
                                 book_prices,
                                 plot_base64,
                                 book_in_book_store.get_full_url(),
                                 return_url)
