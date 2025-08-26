from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, CHAR, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped


class BaseModel(DeclarativeBase):
    pass


class ApiKey(BaseModel):
    __tablename__ = 'ApiKey'
    id = Column('Id', Integer, primary_key=True, autoincrement=True)
    api_name = Column('ApiName', String(255), nullable=False)
    api_user = Column('ApiUser', String(255), nullable=False)
    api_key = Column('ApiKey', String(1024), nullable=False)
    updated = Column('updated', TIMESTAMP, nullable=True)


class Book(BaseModel):
    __tablename__ = 'Book'
    id = Column('Id', Integer, primary_key=True, autoincrement=True)
    isbn = Column('Isbn', String(13), nullable=False, unique=True, default='')
    title = Column('Title', String(255), nullable=False)
    author = Column('Author', String(255), nullable=False)
    format = Column('Format', String(255), nullable=False, default='')
    image_url = Column('ImageUrl', String(255), nullable=True)
    created = Column('Created', DateTime, nullable=False, default='0001-01-01 00:00:00')


class BookPrice(BaseModel):
    __tablename__ = 'BookPrice'
    id = Column('Id', Integer, primary_key=True, autoincrement=True)
    book_id = Column('BookId', Integer, ForeignKey('Book.Id', ondelete='CASCADE'), nullable=True)
    book_store_id = Column('BookStoreId', Integer, ForeignKey('BookStore.Id', ondelete='CASCADE'), nullable=True)
    price = Column('Price', Float(precision=2), nullable=False)
    created = Column('Created', DateTime, nullable=False)


class BookStore(BaseModel):
    __tablename__ = 'BookStore'
    id = Column('Id', Integer, primary_key=True, autoincrement=True)
    name = Column('Name', String(255), nullable=False)
    url = Column('Url', String(255), nullable=False)
    search_url = Column('SearchUrl', String(255), nullable=True)
    search_result_css_selector = Column('SearchResultCssSelector', String(255), nullable=True)
    price_css_selector = Column('PriceCssSelector', String(255), nullable=True)
    image_css_selector = Column('ImageCssSelector', String(255), nullable=True)
    isbn_css_selector = Column('IsbnCssSelector', String(255), nullable=True)
    price_format = Column('PriceFormat', String(80), nullable=True)
    has_dynamically_loaded_content = Column('HasDynamicallyLoadedContent', Boolean, nullable=False)
    color_hex = Column('ColorHex', CHAR(6), nullable=True)


class BookStoreBook(BaseModel):
    __tablename__ = 'BookStoreBook'
    book_id = Column(
        'BookId', Integer, ForeignKey('Book.Id', ondelete='CASCADE'), primary_key=True)
    book_store_id = Column(
        'BookStoreId', Integer, ForeignKey('BookStore.Id', ondelete='CASCADE'), primary_key=True)
    url = Column('Url', String(255), nullable=False)


class BookList(BaseModel):
    __tablename__ = 'BookList'
    id = Column('Id', Integer, primary_key=True, autoincrement=True)
    user_id = Column('UserId', CHAR(36), ForeignKey('User.Id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    name = Column('Name', String(255), nullable=False)
    description = Column('Description', String(512), nullable=True)
    created = Column('Created', DateTime, nullable=False)
    updated = Column('Updated', DateTime, nullable=False)

    books: Mapped[list["BookListBook"]] = relationship("BookListBook")


class BookListBook(BaseModel):
    __tablename__ = 'BookListBook'
    booklist_id = Column(
        'BookListId',
        Integer,
        ForeignKey('BookList.Id', ondelete='CASCADE', onupdate='CASCADE'),
        primary_key=True)
    book_id = Column(
        'BookId',
        Integer,
        ForeignKey('Book.Id', ondelete='CASCADE', onupdate='CASCADE'),
        primary_key=True)
    created = Column('Created', DateTime, nullable=False)

    book: Mapped[Book] = relationship("Book", uselist=False)


class BookStoreSitemap(BaseModel):
    __tablename__ = 'BookStoreSitemap'
    id = Column('Id', Integer, primary_key=True, autoincrement=True)
    book_store_id = Column(
        'BookStoreId',
        Integer,
        ForeignKey('BookStore.Id', ondelete='CASCADE'),
        nullable=False)
    url = Column('Url', String(255), nullable=False)


class FailedPriceUpdate(BaseModel):
    __tablename__ = 'FailedPriceUpdate'
    id = Column('Id', Integer, primary_key=True, autoincrement=True)
    book_id = Column('BookId', Integer, ForeignKey('Book.Id', ondelete='CASCADE'), nullable=False)
    book_store_id = Column(
        'BookStoreId', Integer, ForeignKey('BookStore.Id', ondelete='CASCADE'), nullable=False)
    reason = Column('Reason', String(100), nullable=False)
    created = Column('Created', DateTime, nullable=False)


class User(BaseModel):
    __tablename__ = 'User'
    id = Column('Id', String(100), primary_key=True)
    email = Column('Email', String(255), unique=True, nullable=False)
    first_name = Column('FirstName', String(255), nullable=False)
    last_name = Column('LastName', String(255), nullable=True)
    is_active = Column('IsActive', Boolean, nullable=False)
    google_api_token = Column('GoogleApiToken', String(512), nullable=False)
    created = Column('Created', DateTime, nullable=False)
    updated = Column('Updated', DateTime, nullable=False)
    image_url = Column('ImageUrl', String(255), nullable=True)
    access_level = Column('AccessLevel', Integer, nullable=False, default=1)
    booklist_id = Column('BookListId', Integer, ForeignKey('BookList.Id', ondelete='SET NULL'), nullable=True)
