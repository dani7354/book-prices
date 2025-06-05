import dataclasses

from flask import url_for, request

from bookprices.shared.model.user import UserAccessLevel
from bookprices.web.service.auth_service import AuthService
from bookprices.web.shared.enum import Endpoint


@dataclasses.dataclass(frozen=True)
class MenuItem:
    url: str
    title: str
    is_active: bool
    order_number: int


class SiteMenuService:
    """" Service that provides menu items for the site """

    def __init__(self, auth_service: AuthService) -> None:
        self._auth_service = auth_service


    def get_menu_items(self) -> list[MenuItem]:
        items = []
        current_url = self.get_current_request_path()
        if self._auth_service.user_can_access(UserAccessLevel.MEMBER):
            items.append(
                MenuItem(
                    url=self.get_url(Endpoint.USER_INDEX),
                    title="Rediger bruger",
                    is_active=current_url.startswith(self.get_url(Endpoint.USER_INDEX)),
                    order_number=10)
            )
        if self._auth_service.user_can_access(UserAccessLevel.JOB_MANAGER):
            items.append(
                MenuItem(
                    url=self.get_url(Endpoint.JOB_INDEX),
                    title="Job",
                    is_active=current_url.startswith(self.get_url(Endpoint.JOB_INDEX)),
                    order_number=15)
            )
        if self._auth_service.user_can_access(UserAccessLevel.ADMIN):
            items.extend([
                MenuItem(
                    url=self.get_url(Endpoint.BOOK_CREATE),
                    title="Tilføj bog",
                    is_active=current_url.startswith(self.get_url(Endpoint.BOOK_CREATE)),
                    order_number=12),
                MenuItem(
                    url=self.get_url(Endpoint.STATUS_INDEX),
                    title="Status",
                    is_active=current_url.startswith(self.get_url(Endpoint.STATUS_INDEX)),
                    order_number=20)
            ])

        return sorted(items, key=lambda item: item.order_number)

    @staticmethod
    def get_current_request_path() -> str:
        return request.path if request else ""

    @staticmethod
    def get_url(endpoint: Endpoint) -> str:
        return url_for(endpoint.value)



