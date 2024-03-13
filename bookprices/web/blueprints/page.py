import flask_login
import bookprices.shared.db.database as database
import bookprices.web.mapper.book as bookmapper
import bookprices.web.mapper.user as usermapper
from bookprices.shared.db.book import SearchQuery
from bookprices.shared.model.book import Book
from bookprices.web.cache.redis import cache
from bookprices.web.blueprints.urlhelper import parse_args_for_search, format_url_for_redirection
from flask import render_template, request, abort, Blueprint, redirect, Response, url_for, session
from flask_login import current_user
from bookprices.web.service import csrf
from bookprices.web.service.auth_service import AuthService
from bookprices.web.viewmodels.book import CreateBookViewModel
from bookprices.web.viewmodels.page import AboutViewModel
from bookprices.web.cache.key_generator import (
    get_authors_key,
    get_bookstores_key,
    get_index_latest_books_key,
    get_index_latest_prices_books_key,
    get_book_key,
    get_book_list_key,
    get_book_in_book_store_key,
    get_book_latest_prices_key)
from bookprices.web.settings import (
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_USER,
    MYSQL_PASSWORD,
    MYSQL_DATABASE,
    AUTHOR_URL_PARAMETER,
    SEARCH_URL_PARAMETER,
    PAGE_URL_PARAMETER,
    BOOK_PAGESIZE,
    ORDER_BY_URL_PARAMETER,
    DESCENDING_URL_PARAMETER)
from bookprices.web.viewmodels.user import UserEditViewModel

NOT_FOUND = 404
INTERNAL_SERVER_ERROR = 500

page_blueprint = Blueprint("page", __name__)

db = database.Database(MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)
auth_service = AuthService(db, cache)


@page_blueprint.context_processor
def include_csrf_token() -> dict[str, str]:
    csrf_service = csrf.CSRFService()
    csrf_token = csrf_service.generate_token()

    return {"csrf_token": csrf_token}


@page_blueprint.route("/")
def index() -> str:
    if not (newest_books := cache.get(get_index_latest_books_key())):
        newest_books = db.book_db.get_newest_books(limit=8)
        cache.set(get_index_latest_books_key(), newest_books)
    if not (newest_prices_books := cache.get(get_index_latest_prices_books_key())):
        newest_prices_books = db.book_db.get_books_with_newest_prices(limit=8)
        cache.set(get_index_latest_prices_books_key(), newest_prices_books)
    view_model = bookmapper.map_index_vm(newest_books=newest_books, latest_updated_books=newest_prices_books)

    return render_template("index.html", view_model=view_model)


@page_blueprint.route("/about")
def about() -> str:
    bookstores_cache_key = get_bookstores_key()
    if not (bookstores := cache.get(bookstores_cache_key)):
        bookstores = db.bookstore_db.get_bookstores()
        cache.set(bookstores_cache_key, bookstores)
    view_model = AboutViewModel(bookstores)

    return render_template("about.html", view_model=view_model)


@page_blueprint.route("/search")
def search() -> str:
    args = parse_args_for_search(request.args)
    author = args.get(AUTHOR_URL_PARAMETER)
    search_phrase = args.get(SEARCH_URL_PARAMETER)
    order_by = args.get(ORDER_BY_URL_PARAMETER)
    descending = args.get(DESCENDING_URL_PARAMETER)
    page = args.get(PAGE_URL_PARAMETER)

    if not (authors := cache.get(get_authors_key())):
        authors = db.book_db.get_authors()
        cache.set(get_authors_key(), authors)

    query = SearchQuery(search_phrase=search_phrase,
                        author=author,
                        page=page,
                        page_size=BOOK_PAGESIZE,
                        sort_option=order_by,
                        sort_in_descending_order=descending)
    books_current_cache_key = get_book_list_key(query)
    if not (books_current := cache.get(books_current_cache_key)):
        books_current = db.book_db.search_books(query)
        cache.set(books_current_cache_key, books_current)

    next_query = query.clone(page=page + 1)
    books_next_cache_key = get_book_list_key(next_query)
    if not (books_next := cache.get(books_next_cache_key)):
        books_next = db.book_db.search_books(next_query)
        cache.set(books_next_cache_key, books_next)

    next_page = page + 1 if len(books_next) > 0 else None
    previous_page = page - 1 if page >= 2 else None

    vm = bookmapper.map_search_vm(books_current,
                                  authors,
                                  search_phrase,
                                  page,
                                  author,
                                  previous_page,
                                  next_page,
                                  order_by,
                                  descending)

    return render_template("search.html", view_model=vm)


@page_blueprint.route("/book/<int:book_id>")
def book(book_id: int) -> str:
    cache_key = get_book_key(book_id)
    if not (book := cache.get(cache_key)):
        if not book and not (book := db.book_db.get_book(book_id)):
            abort(NOT_FOUND)
        cache.set(cache_key, book)

    args = parse_args_for_search(request.args)
    page = args.get(PAGE_URL_PARAMETER)
    search_phrase = args.get(SEARCH_URL_PARAMETER)
    author = args.get(AUTHOR_URL_PARAMETER)
    order_by = args.get(ORDER_BY_URL_PARAMETER)
    descending = args.get(DESCENDING_URL_PARAMETER)

    if not (latest_prices := cache.get(get_book_latest_prices_key(book_id))):
        latest_prices = db.bookprice_db.get_latest_prices(book.id)
        cache.set(get_book_latest_prices_key(book_id), latest_prices)

    book_details = bookmapper.map_book_details(book,
                                               latest_prices,
                                               page,
                                               author,
                                               search_phrase,
                                               order_by,
                                               descending)

    return render_template("book.html", view_model=book_details)


@page_blueprint.route("/book/create", methods=["GET", "POST"])
@flask_login.login_required
def create() -> str | Response:
    if request.method == "POST":
        view_model = CreateBookViewModel(
            isbn=isbn.strip() if (isbn := request.form.get(CreateBookViewModel.isbn_field_name)) else "",
            title=title.strip() if (title := request.form.get(CreateBookViewModel.title_field_name)) else "",
            author=author.strip() if (author := request.form.get(CreateBookViewModel.author_field_name)) else "",
            format=book_format.strip() if (book_format := request.form.get(CreateBookViewModel.format_field_name)) else "")
        if not view_model.is_valid():
            return render_template("create_book.html", view_model=view_model)
        if db.book_db.get_book_by_isbn(view_model.isbn):
            view_model.add_error(view_model.isbn_field_name, "Bogen findes allerede")
            return render_template("create_book.html", view_model=view_model)

        book_id = db.book_db.create_book(
            Book(id=0,
                 isbn=view_model.isbn,
                 title=view_model.title,
                 author=view_model.author,
                 format=view_model.format))

        return redirect(url_for("page.book", book_id=book_id))

    return render_template("create_book.html", view_model=CreateBookViewModel.empty())


@page_blueprint.route("/book/<int:book_id>/store/<int:store_id>")
def price_history(book_id: int, store_id: int) -> str:
    book_cache_key = get_book_key(book_id)
    if not (book := cache.get(book_cache_key)):
        if not book and not (book := db.book_db.get_book(book_id)):
            abort(NOT_FOUND)
        cache.set(book_cache_key, book)

    book_bookstore_cache_key = get_book_in_book_store_key(book_id, store_id)
    if not (book_in_bookstore := cache.get(book_bookstore_cache_key)):
        if not book_in_bookstore and not (book_in_bookstore := db.bookstore_db.get_bookstore_for_book(book, store_id)):
            abort(NOT_FOUND)
        cache.set(book_bookstore_cache_key, book_in_bookstore)

    args = parse_args_for_search(request.args)
    page = args.get(PAGE_URL_PARAMETER)
    search_phrase = args.get(SEARCH_URL_PARAMETER)
    author = args.get(AUTHOR_URL_PARAMETER)
    order_by = args.get(ORDER_BY_URL_PARAMETER)
    descending = args.get(DESCENDING_URL_PARAMETER)

    price_history_view_model = bookmapper.map_price_history(book_in_bookstore,
                                                            page,
                                                            search_phrase,
                                                            author,
                                                            order_by,
                                                            descending)

    return render_template("price_history.html", view_model=price_history_view_model)


@page_blueprint.route("/login")
def login() -> Response | str:
    redirect_url = redirect_url if (redirect_url := format_url_for_redirection(request.args.get("next"))) \
        else url_for("page.index")
    if current_user.is_authenticated:
        return redirect(redirect_url)

    return render_template("login.html", redirect_url=redirect_url)


@page_blueprint.route("/admin")
@flask_login.login_required
def admin() -> str:
    return render_template("admin.html")


@page_blueprint.route("/user", methods=["GET", "POST"])
@flask_login.login_required
def user() -> str:
    if request.method == "POST":
        view_model = UserEditViewModel(
            id=flask_login.current_user.id,
            email=email.strip() if (email := request.form.get(UserEditViewModel.email_field_name)) else "",
            firstname=firstname.strip() if (firstname := request.form.get(UserEditViewModel.firstname_field_name)) else "",
            lastname=lastname.strip() if (lastname := request.form.get(UserEditViewModel.lastname_field_name)) else "",
            is_active=True if request.form.get(UserEditViewModel.is_active_field_name) else False)

        if not view_model.is_valid():
            return render_template("user.html", view_model=view_model)

        auth_service.update_user_info(
            view_model.id,
            view_model.email,
            view_model.firstname,
            view_model.lastname,
            view_model.is_active)
    else:
        view_model = usermapper.map_user_view_model(flask_login.current_user)

    return render_template("user.html", view_model=view_model)


@page_blueprint.errorhandler(NOT_FOUND)
def not_found(error) -> tuple[str, int]:
    return render_template("404.html"), NOT_FOUND


@page_blueprint.errorhandler(INTERNAL_SERVER_ERROR)
def internal_server_error(error) -> tuple[str, int]:
    return render_template("500.html"), INTERNAL_SERVER_ERROR
