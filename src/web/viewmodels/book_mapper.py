from .book import BookListItemViewModel, BookDetailsViewModel, PriceHistoryViewModel


class BookMapper:
    @classmethod
    def map_book_list(cls, books) -> list:
        return [cls.map_book_list_item(b) for b in books]

    @staticmethod
    def map_book_list_item(book) -> BookListItemViewModel:
        return BookListItemViewModel(book.id, book.title, book.author)

    @staticmethod
    def map_book_details(book, book_prices) -> BookDetailsViewModel:
        return BookDetailsViewModel(book, book_prices)

    @staticmethod
    def map_price_history(book_in_book_store, book_prices):

        return PriceHistoryViewModel(book_in_book_store.book,
                                     book_in_book_store.book_store,
                                     book_prices,
                                     book_in_book_store.get_full_url())
