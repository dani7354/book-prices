from typing import Sequence

import flask
from flask import url_for

from bookprices.shared.model.bookstore import BookStore
from bookprices.web.shared.enum import Endpoint
from bookprices.web.viewmodels.bookstore import BookStoreListViewModel, BookStoreListItem, BookStoreEditViewModel


def map_to_bookstore_list(
        bookstores: Sequence[BookStore],
        current_user_is_admin: bool) -> BookStoreListViewModel:
    return BookStoreListViewModel(
        can_edit=current_user_is_admin,
        can_delete=current_user_is_admin,
        create_url=url_for(Endpoint.BOOKSTORE_CREATE.value),
        bookstores=[
            BookStoreListItem(
                id=bookstore.id,
                name=bookstore.name,
                url=bookstore.url,
                edit_url=url_for(Endpoint.BOOKSTORE_EDIT.value, bookstore_id=bookstore.id)
            ) for bookstore in bookstores])


def map_bookstore_edit_view_model(bookstore: BookStore) -> BookStoreEditViewModel:
    return BookStoreEditViewModel(
        has_dynamic_content=bookstore.has_dynamically_loaded_content,
        id=bookstore.id,
        name=bookstore.name,
        url=bookstore.url,
        search_url=bookstore.search_url,
        search_result_css=bookstore.search_result_css_selector,
        image_css=bookstore.image_css_selector,
        isbn_css=bookstore.isbn_css_selector,
        price_css=bookstore.price_css_selector,
        price_format=bookstore.price_format,
        form_action_url=url_for(Endpoint.BOOKSTORE_EDIT.value, bookstore_id=bookstore.id),
        return_url=url_for(Endpoint.BOOKSTORE_INDEX.value))


def map_bookstore_edit_view_model_from_form(
        request: flask.Request, form_action_url: str, return_url: str, bookstore_id=0) -> BookStoreEditViewModel:
    bookstore_id_from_form = request.form.get(BookStoreEditViewModel.id_field_name) or bookstore_id
    name = request.form.get(BookStoreEditViewModel.name_field_name) or ""
    url = request.form.get(BookStoreEditViewModel.url_field_name) or ""
    search_url = request.form.get(BookStoreEditViewModel.search_url_field_name) or None
    search_result_css = request.form.get(BookStoreEditViewModel.search_result_css_field_name) or None
    image_css = request.form.get(BookStoreEditViewModel.image_css_field_name) or None
    isbn_css = request.form.get(BookStoreEditViewModel.isbn_css_field_name) or None
    price_css = request.form.get(BookStoreEditViewModel.price_css_field_name) or None
    price_format = request.form.get(BookStoreEditViewModel.price_format_field_name) or None
    has_dynamic_content = bool(request.form.get(BookStoreEditViewModel.has_dynamic_content_field_name)) or False

    return BookStoreEditViewModel(
        id=bookstore_id_from_form,
        name=name,
        url=url,
        search_url=search_url,
        search_result_css=search_result_css,
        image_css=image_css,
        isbn_css=isbn_css,
        price_css=price_css,
        price_format=price_format,
        has_dynamic_content=has_dynamic_content,
        form_action_url=form_action_url,
        return_url=return_url)
