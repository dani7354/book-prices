from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, CHAR, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase


class BaseModel(DeclarativeBase):
    pass


class ApiKey(BaseModel):
    __tablename__ = 'ApiKey'
    Id = Column(Integer, primary_key=True, autoincrement=True)
    ApiName = Column(String(255), nullable=False)
    ApiUser = Column(String(255), nullable=False)
    ApiKey = Column(String(1024), nullable=False)
    updated = Column(TIMESTAMP, nullable=True)


class Book(BaseModel):
    __tablename__ = 'Book'
    Id = Column(Integer, primary_key=True, autoincrement=True)
    Isbn = Column(String(13), nullable=False, unique=True, default='')
    Title = Column(String(255), nullable=False)
    Author = Column(String(255), nullable=False)
    Format = Column(String(255), nullable=False, default='')
    ImageUrl = Column(String(255), nullable=True)
    Created = Column(DateTime, nullable=False, default='0001-01-01 00:00:00')


class BookPrice(BaseModel):
    __tablename__ = 'BookPrice'
    Id = Column(Integer, primary_key=True, autoincrement=True)
    BookId = Column(Integer, ForeignKey('Book.Id', ondelete='CASCADE'), nullable=True)
    BookStoreId = Column(Integer, ForeignKey('BookStore.Id', ondelete='CASCADE'), nullable=True)
    Price = Column(Float(precision=2), nullable=False)
    Created = Column(DateTime, nullable=False)


class BookStore(BaseModel):
    __tablename__ = 'BookStore'
    Id = Column(Integer, primary_key=True, autoincrement=True)
    Name = Column(String(255), nullable=False)
    Url = Column(String(255), nullable=False)
    SearchUrl = Column(String(255), nullable=True)
    SearchResultCssSelector = Column(String(255), nullable=True)
    PriceCssSelector = Column(String(255), nullable=True)
    ImageCssSelector = Column(String(255), nullable=True)
    IsbnCssSelector = Column(String(255), nullable=True)
    PriceFormat = Column(String(80), nullable=True)
    HasDynamicallyLoadedContent = Column(Boolean, nullable=False)
    ColorHex = Column(CHAR(6), nullable=True)


class BookStoreBook(BaseModel):
    __tablename__ = 'BookStoreBook'
    BookId = Column(Integer, ForeignKey('Book.Id', ondelete='CASCADE'), primary_key=True)
    BookStoreId = Column(Integer, ForeignKey('BookStore.Id', ondelete='CASCADE'), primary_key=True)
    Url = Column(String(255), nullable=False)


class BookList(BaseModel):
    __tablename__ = 'BookList'
    Id = Column(Integer, primary_key=True, autoincrement=True)
    UserId = Column(CHAR(36), ForeignKey('User.Id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    Name = Column(String(255), nullable=False)
    Created = Column(DateTime, nullable=False)
    Updated = Column(DateTime, nullable=False)


class BookListBook(BaseModel):
    __tablename__ = 'BookListBook'
    BookListId = Column(Integer, ForeignKey('BookList.Id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    BookId = Column(Integer, ForeignKey('Book.Id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    Created = Column(DateTime, nullable=False)


class BookStoreSitemap(BaseModel):
    __tablename__ = 'BookStoreSitemap'
    Id = Column(Integer, primary_key=True, autoincrement=True)
    BookStoreId = Column(Integer, ForeignKey('BookStore.Id', ondelete='CASCADE'), nullable=False)
    Url = Column(String(255), nullable=False)


class FailedPriceUpdate(BaseModel):
    __tablename__ = 'FailedPriceUpdate'
    Id = Column(Integer, primary_key=True, autoincrement=True)
    BookId = Column(Integer, ForeignKey('Book.Id', ondelete='CASCADE'), nullable=False)
    BookStoreId = Column(Integer, ForeignKey('BookStore.Id', ondelete='CASCADE'), nullable=False)
    Reason = Column(String(100), nullable=False)
    Created = Column(DateTime, nullable=False)


class User(BaseModel):
    __tablename__ = 'User'
    Id = Column(String(100), primary_key=True)
    Email = Column(String(255), unique=True, nullable=False)
    FirstName = Column(String(255), nullable=False)
    LastName = Column(String(255), nullable=True)
    IsActive = Column(Boolean, nullable=False)
    GoogleApiToken = Column(String(255), nullable=False)
    Created = Column(DateTime, nullable=False)
    Updated = Column(DateTime, nullable=False)
    ImageUrl = Column(String(255), nullable=True)
    AccessLevel = Column(Integer, nullable=False, default=1)
