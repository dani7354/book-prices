from functools import wraps

import flask_login
from datetime import datetime

from flask import abort
from flask_caching import Cache
from typing import Optional, ClassVar
from bookprices.shared.db. database import Database
from bookprices.shared.model.user import User, UserAccessLevel
from bookprices.shared.cache.key_generator import get_user_key
from bookprices.web.shared.enum import HttpStatusCode


class WebUser(flask_login.UserMixin):
    def __init__(self, user_model: User):
        self._user_model = user_model

    @property
    def id(self) -> str:
        return self._user_model.id

    @property
    def is_active(self) -> bool:
        return self._user_model.is_active

    @property
    def email(self) -> str:
        return self._user_model.email

    @property
    def firstname(self) -> str:
        return self._user_model.firstname

    @property
    def lastname(self) -> str:
        return self._user_model.lastname

    @property
    def created(self) -> datetime:
        return self._user_model.created

    @property
    def updated(self) -> datetime:
        return self._user_model.updated

    @property
    def google_api_token(self) -> str:
        return self._user_model.google_api_token

    @property
    def image_url(self) -> str:
        return self._user_model.image_url

    @property
    def access_level(self) -> UserAccessLevel:
        return self._user_model.access_level

    def get_id(self) -> str:
        return self.id


class AuthService:
    max_users_per_page: ClassVar[int] = 20

    def __init__(self, db: Database, cache: Cache):
        self._db = db
        self._cache = cache

    def get_user(self, user_id: str) -> Optional[WebUser]:
        if not (user := self._cache.get(get_user_key(user_id))):
            user = self._db.user_db.get_user_by_id(user_id)
            if user:
                self._cache.set(get_user_key(user_id), user)
        return WebUser(user) if user else None

    def get_users(self, page: int) -> list[WebUser]:
        offset = (page - 1) * self.max_users_per_page
        users = self._db.user_db.get_users(self.max_users_per_page, offset)

        return [WebUser(user) for user in users] if users else []

    def update_user_token_and_image_url(self, user_id: str, token: str, image_url: str) -> None:
        self._db.user_db.update_user_token_and_image_url(user_id, token, image_url)
        self._cache.delete(get_user_key(user_id))

    def create_user(self, id_: str, email: str, access_token: str, image_url: str) -> None:
        new_user = User(
            id=id_,
            email=email,
            firstname=email,
            lastname=None,
            is_active=True,
            google_api_token=access_token,
            image_url=image_url,
            access_level=UserAccessLevel.MEMBER,
            created=datetime.now(),
            updated=datetime.now())

        self._db.user_db.create_user(new_user)

    def update_user_info(
            self, user_id:
            str, email: str,
            firstname: str,
            lastname: str,
            access_level: UserAccessLevel,
            is_active: bool) -> None:
        self._db.user_db.update_user_info(
            user_id=user_id,
            email=email,
            firstname=firstname,
            lastname=lastname,
            is_active=is_active,
            access_level=access_level.value)

        self._cache.delete(get_user_key(user_id))

    @classmethod
    def user_can_access(cls, access_level: UserAccessLevel) -> bool:
        current_user = cls.get_current_user()
        return (current_user and
                current_user.is_authenticated and
                current_user.access_level.value >= access_level.value)

    @staticmethod
    def get_current_user() -> Optional[WebUser]:
        if current_user := flask_login.current_user:
            return WebUser(current_user)

        return None


def require_admin(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if not AuthService.user_can_access(UserAccessLevel.ADMIN):
            return abort(HttpStatusCode.FORBIDDEN)
        return func(*args, **kwargs)

    return decorated


def require_job_manager(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if not AuthService.user_can_access(UserAccessLevel.JOB_MANAGER):
            return abort(HttpStatusCode.FORBIDDEN)
        return func(*args, **kwargs)

    return decorated


def require_member(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if not AuthService.user_can_access(UserAccessLevel.MEMBER):
            return abort(HttpStatusCode.FORBIDDEN)
        return func(*args, **kwargs)

    return decorated
