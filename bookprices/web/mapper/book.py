import os
import bookprices.web.viewmodels.book as view_model
from typing import Optional
from bookprices.shared.model.book import Book
from bookprices.shared.model.bookprice import BookPrice
from bookprices.shared.model.bookstore import BookStoreBookPrice, BookInBookStore

PRICE_NONE_TEXT = "-"
PRICE_CREATED_NONE_TEXT = "Pris ikke hentet"


class BookMapper:
    @classmethod
    def map_index_vm(cls,
                     books: list[Book],
                     authors: list[str],
                     search_phrase: str,
                     image_base_url: str,
                     fallback_image: str,
                     current_page: int,
                     previous_page: Optional[int],
                     next_page: Optional[int]) -> view_model.IndexViewModel:

        return view_model.IndexViewModel(cls.map_book_list(books, image_base_url, fallback_image),
                                         authors,
                                         search_phrase,
                                         current_page,
                                         previous_page,
                                         next_page)

    @classmethod
    def map_book_list(cls,
                      books: list[Book],
                      image_base_url: str,
                      fallback_image: str) -> list[view_model.BookListItemViewModel]:

        return [cls.map_book_list_item(b, image_base_url, fallback_image) for b in books]

    @staticmethod
    def map_book_list_item(book: Book, image_base_url: str, fallback_image: str) -> view_model.BookListItemViewModel:

        if book.image_url is not None:
            image_url = os.path.join(image_base_url, book.image_url)
        else:
            image_url = os.path.join(image_base_url, fallback_image)

        return view_model.BookListItemViewModel(book.id, book.isbn, book.title, book.author, image_url)

    @staticmethod
    def map_book_details(book: Book,
                         book_prices: list[BookStoreBookPrice],
                         image_base_url: str,
                         fallback_image: str,
                         plot_data: str,
                         index_url: str,
                         page: Optional[int],
                         search_phrase: Optional[str]) -> view_model.BookDetailsViewModel:

        book_price_view_models = []
        for bp in book_prices:
            is_price_available = bp.price is not None
            price_str = bp.price if is_price_available else PRICE_NONE_TEXT
            created_str = bp.created if is_price_available else PRICE_CREATED_NONE_TEXT

            book_price_view_models.append(view_model.BookPriceForStoreViewModel(bp.book_store_id,
                                                                                bp.book_store_name,
                                                                                bp.url,
                                                                                price_str,
                                                                                created_str,
                                                                                is_price_available))

        if book.image_url is not None:
            book.image_url = os.path.join(image_base_url, book.image_url)
        else:
            book.image_url = os.path.join(image_base_url, fallback_image)

        return view_model.BookDetailsViewModel(book,
                                               book_price_view_models,
                                               plot_data,
                                               index_url,
                                               page,
                                               search_phrase)

    @staticmethod
    def map_price_history(book_in_book_store: BookInBookStore,
                          book_prices: list[BookPrice],
                          return_url: str,
                          plot_base64: str) -> view_model.PriceHistoryViewModel:

        return view_model.PriceHistoryViewModel(book_in_book_store.book,
                                                book_in_book_store.book_store,
                                                book_prices,
                                                plot_base64,
                                                book_in_book_store.get_full_url(),
                                                return_url)
