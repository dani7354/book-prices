from typing import Optional

from flask import url_for

from bookprices.web.service.auth_service import WebUser
from bookprices.web.shared.enum import UserTemplate, Endpoint
from bookprices.web.viewmodels.user import UserEditViewModel, UserListViewModel, UserListItemViewModel


def map_user_view_model(user: WebUser, form_action_url: str, edit_current_user: bool) -> UserEditViewModel:
    lastname = user.lastname if user.lastname else ""
    return UserEditViewModel(
        id=user.id,
        created=user.created.isoformat(),
        updated=user.updated.isoformat(),
        email=user.email,
        firstname=user.firstname,
        lastname=lastname,
        is_active=user.is_active,
        edit_current_user=edit_current_user,
        image_url=user.image_url,
        access_level=user.access_level.name,
        form_action_url=form_action_url,
        return_url=url_for(Endpoint.USER_INDEX.value) if not edit_current_user else None)


def map_user_list_view_model(
        users: list[WebUser],
        page: int,
        previous_page: Optional[int],
        next_page: Optional[int],
        user_can_edit: bool,
        user_can_delete: bool) -> UserListViewModel:
    user_view_models = [
        UserListItemViewModel(
            id=u.id,
            email=u.email,
            firstname=u.firstname,
            lastname=u.lastname if u.lastname else "",
            is_active=u.is_active,
            access_level=u.access_level.name,
            edit_url=url_for('user.edit', user_id=u.id),
            created=u.created.isoformat(),
            updated=u.updated.isoformat())
        for u in users]

    next_page_url = url_for(UserTemplate.INDEX.value, page=next_page) if next_page else None
    previous_page_url = url_for(UserTemplate.INDEX.value, page=previous_page) if previous_page else None

    return UserListViewModel(
        can_edit=user_can_edit,
        can_delete=user_can_delete,
        current_page=page,
        next_page_url=next_page_url,
        previous_page_url=previous_page_url,
        users=user_view_models)

