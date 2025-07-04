import uuid
import pytest
from datetime import datetime
from unittest.mock import Mock

from bookprices.shared.config.config import Cache
from bookprices.shared.db.database import Database
from bookprices.shared.model.user import User, UserAccessLevel
from bookprices.web.service.auth_service import AuthService, WebUser
from bookprices.web.service.site_menu_service import SiteMenuService


@pytest.fixture
def auth_service_mock() -> AuthService:
    auth_service = AuthService(Mock(Database), Mock(Cache))

    return auth_service


def _get_service_with_patched_methods(auth_service: AuthService) -> SiteMenuService:
    service = SiteMenuService(auth_service)
    service.get_current_request_path = lambda: "/"
    service.get_url = lambda endpoint: "/"

    return service


def _get_user_with_access_level(access_level) -> WebUser:
    user = User(
        id=str(uuid.uuid4()),
        email="jens@xyz.com",
        firstname="Jens",
        lastname="Jensen",
        is_active=True,
        google_api_token="<TOKEN>",
        access_level=access_level,
        created=datetime.now(),
        updated=datetime.now(),
        image_url=None)

    web_user = WebUser(user)
    return web_user


@pytest.mark.parametrize(
    ["user_access_level", "number_of_items"],
    [(UserAccessLevel.MEMBER, 1), (UserAccessLevel.JOB_MANAGER, 2), (UserAccessLevel.ADMIN, 6)])
def test_site_menu_service_gives_correct_number_of_items_for_user(
        auth_service_mock: AuthService,
        user_access_level: UserAccessLevel,
        number_of_items: int) -> None:
    AuthService.get_current_user = lambda: _get_user_with_access_level(user_access_level)
    service = _get_service_with_patched_methods(auth_service_mock)

    items = service.get_menu_items()

    assert len(items) == number_of_items


def test_site_menu_services_gives_correct_items_for_member(
        auth_service_mock: AuthService) -> None:
    AuthService.get_current_user = lambda: _get_user_with_access_level(UserAccessLevel.MEMBER)
    service = _get_service_with_patched_methods(auth_service_mock)

    items = service.get_menu_items()

    assert items
    assert items[0].title == "Rediger bruger"


def test_site_menu_services_gives_correct_items_for_job_manager(
        auth_service_mock: AuthService) -> None:
    AuthService.get_current_user = lambda: _get_user_with_access_level(UserAccessLevel.JOB_MANAGER)
    service = _get_service_with_patched_methods(auth_service_mock)

    items = service.get_menu_items()

    assert items
    assert items[0].title == "Rediger bruger"
    assert items[1].title == "Job"


def test_site_menu_services_gives_correct_items_for_admin(
        auth_service_mock: AuthService) -> None:
    AuthService.get_current_user = lambda: _get_user_with_access_level(UserAccessLevel.ADMIN)
    service = _get_service_with_patched_methods(auth_service_mock)

    items = service.get_menu_items()

    assert items
    assert items[0].title == "Rediger bruger"
    assert items[1].title == "Brugere"
    assert items[2].title == "Boghandlere"
    assert items[3].title == "Tilføj bog"
    assert items[4].title == "Job"
    assert items[5].title == "Status"
