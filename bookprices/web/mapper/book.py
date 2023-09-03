import os
from typing import Optional
from urllib.parse import urlencode
from bookprices.web.viewmodels.book import (IndexViewModel, AuthorOption, BookListItemViewModel,                                         BookPriceForStoreViewModel, PriceHistoryViewModel, BookDetailsViewModel)
from bookprices.shared.model.book import Book
from bookprices.shared.model.bookprice import BookPrice
from bookprices.shared.model.bookstore import BookStoreBookPrice, BookInBookStore

PRICE_NONE_TEXT = "-"
PRICE_CREATED_NONE_TEXT = "Pris ikke hentet"
AUTHOR_DEFAULT_OPTION_TEXT = "Alle forfattere"


class BookMapper:
    @classmethod
    def map_index_vm(cls,
                     books: list[Book],
                     authors: list[str],
                     search_phrase: str,
                     image_base_url: str,
                     fallback_image: str,
                     current_page: int,
                     author: Optional[str],
                     previous_page: Optional[int],
                     next_page: Optional[int]) -> IndexViewModel:

        author_options = [AuthorOption(AUTHOR_DEFAULT_OPTION_TEXT, "", not author)]
        for a in authors:
            author_options.append(AuthorOption(a, a, a == author))

        base_url = "/"
        previous_page_url = None
        next_page_url = None
        params = {}
        if search_phrase:
            params["search"] = search_phrase
        if author:
            params["author"] = author

        if previous_page:
            previous_page_url_params = params.copy()
            previous_page_url_params["page"] = str(previous_page)
            previous_page_url = base_url + "?" + urlencode(previous_page_url_params)

        if next_page:
            next_page_url_params = params.copy()
            next_page_url_params["page"] = str(next_page)
            next_page_url = base_url + "?" + urlencode(next_page_url_params)

        return IndexViewModel(cls.map_book_list(books, image_base_url, fallback_image),
                              author_options,
                              search_phrase,
                              author,
                              current_page,
                              previous_page,
                              next_page,
                              previous_page_url,
                              next_page_url)

    @classmethod
    def map_book_list(cls,
                      books: list[Book],
                      image_base_url: str,
                      fallback_image: str) -> list[BookListItemViewModel]:

        return [cls.map_book_list_item(b, image_base_url, fallback_image) for b in books]

    @staticmethod
    def map_book_list_item(book: Book, image_base_url: str, fallback_image: str) -> BookListItemViewModel:

        if book.image_url is not None:
            image_url = os.path.join(image_base_url, book.image_url)
        else:
            image_url = os.path.join(image_base_url, fallback_image)

        return BookListItemViewModel(book.id, book.isbn, book.title, book.author, image_url)

    @staticmethod
    def map_book_details(book: Book,
                         book_prices: list[BookStoreBookPrice],
                         image_base_url: str,
                         fallback_image: str,
                         plot_data: str,
                         index_url: str,
                         page: Optional[int],
                         search_phrase: Optional[str]) -> BookDetailsViewModel:

        book_price_view_models = []
        for bp in book_prices:
            is_price_available = bp.price is not None
            price_str = bp.price if is_price_available else PRICE_NONE_TEXT
            created_str = bp.created if is_price_available else PRICE_CREATED_NONE_TEXT

            book_price_view_models.append(BookPriceForStoreViewModel(bp.book_store_id,
                                                                     bp.book_store_name,
                                                                     bp.url,
                                                                     price_str,
                                                                     created_str,
                                                                     is_price_available))

        if book.image_url is not None:
            book.image_url = os.path.join(image_base_url, book.image_url)
        else:
            book.image_url = os.path.join(image_base_url, fallback_image)

        return BookDetailsViewModel(book,
                                    book_price_view_models,
                                    plot_data,
                                    index_url,
                                    page,
                                    search_phrase)

    @staticmethod
    def map_price_history(book_in_book_store: BookInBookStore,
                          book_prices: list[BookPrice],
                          return_url: str,
                          plot_base64: str) -> PriceHistoryViewModel:

        return PriceHistoryViewModel(book_in_book_store.book,
                                     book_in_book_store.book_store,
                                     book_prices,
                                     plot_base64,
                                     book_in_book_store.get_full_url(),
                                     return_url)
