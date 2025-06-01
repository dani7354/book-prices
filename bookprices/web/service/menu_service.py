import dataclasses

import flask_login
from flask import url_for, request

from bookprices.shared.model.user import UserAccessLevel
from bookprices.web.service.auth_service import WebUser, AuthService
from bookprices.web.shared.enum import Endpoint


@dataclasses.dataclass(frozen=True)
class MenuItem:
    url: str
    title: str
    is_active: bool


class SiteMenuService:
    """" Service that provides menu items for the site """

    def __init__(self, auth_service: AuthService) -> None:
        self._auth_service = auth_service


    def get_menu_items(self) -> list[MenuItem]:
        items = []
        current_url = request.path
        if self._auth_service.user_can_access(UserAccessLevel.MEMBER):
            items.append(
                MenuItem(
                    url=url_for(Endpoint.USER_INDEX.value),
                    title="Rediger bruger",
                    is_active=current_url.startswith(url_for(Endpoint.USER_INDEX.value)))
            )
        if self._auth_service.user_can_access(UserAccessLevel.JOB_MANAGER):
            items.append(
                MenuItem(
                    url=url_for(Endpoint.JOB_INDEX.value),
                    title="Job",
                    is_active=current_url.startswith(url_for(Endpoint.JOB_INDEX.value)))
            )
        if self._auth_service.user_can_access(UserAccessLevel.ADMIN):
            items.extend([
                MenuItem(
                    url=url_for(Endpoint.BOOK_CREATE.value),
                    title="Tilføj bog",
                    is_active=current_url.startswith(url_for(Endpoint.BOOK_CREATE.value))),
                MenuItem(
                    url=url_for(Endpoint.STATUS_INDEX.value),
                    title="Status",
                    is_active=current_url.startswith(url_for(Endpoint.STATUS_INDEX.value)))
            ])

        return items



