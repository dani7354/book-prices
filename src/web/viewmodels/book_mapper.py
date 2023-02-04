from .book import BookListItemViewModel, BookDetailsViewModel


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
