from typing import Sequence

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
        price_format=bookstore.price_format,
        form_action_url=url_for(Endpoint.BOOKSTORE_EDIT.value, bookstore_id=bookstore.id),
        return_url=url_for(Endpoint.BOOKSTORE_INDEX.value))
