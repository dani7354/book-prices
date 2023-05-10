class Book:
    def __init__(self, id: int, isbn: str, title: str, author: str, image_url: str | None, created: str | None = None):
        self.id = id
        self.isbn = isbn
        self.title = title
        self.author = author
        self.image_url = image_url
        self.created = created
