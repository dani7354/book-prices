from .book import BookListItemViewModel, BookDetailsViewModel, PriceHistoryViewModel, BookPriceForStoreViewModel

PRICE_NONE_TEXT = "-"
PRICE_CREATED_NONE_TEXT = "Pris ikke hentet"


class BookMapper:
    @classmethod
    def map_book_list(cls, books) -> list:
        return [cls.map_book_list_item(b) for b in books]

    @staticmethod
    def map_book_list_item(book) -> BookListItemViewModel:
        return BookListItemViewModel(book.id, book.title, book.author)

    @staticmethod
    def map_book_details(book, book_prices) -> BookDetailsViewModel:
        book_price_view_models = []
        for bp in book_prices:
            price_str = bp.price if bp.price is not None else PRICE_NONE_TEXT
            created_str = bp.created if bp.created is not None else PRICE_CREATED_NONE_TEXT
            book_price_view_models.append(BookPriceForStoreViewModel(bp.book_store_id,
                                                                     bp.book_store_name,
                                                                     bp.url,
                                                                     price_str,
                                                                     created_str))

        return BookDetailsViewModel(book, book_price_view_models)

    @staticmethod
    def map_price_history(book_in_book_store, book_prices):

        return PriceHistoryViewModel(book_in_book_store.book,
                                     book_in_book_store.book_store,
                                     book_prices,
                                     book_in_book_store.get_full_url())
