import flask_login
from datetime import datetime
from flask_caching import Cache
from typing import Optional
from bookprices.shared.db. database import Database
from bookprices.shared.model.user import User
from bookprices.shared.cache.key_generator import get_user_key


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

    def get_id(self) -> str:
        return self.id


class AuthService:
    def __init__(self, db: Database, cache: Cache):
        self._db = db
        self._cache = cache

    def get_user(self, user_id: str) -> Optional[WebUser]:
        if not (user := self._cache.get(get_user_key(user_id))):
            user = self._db.user_db.get_user_by_id(user_id)
            if user:
                self._cache.set(get_user_key(user_id), user)
        return WebUser(user) if user else None

    def update_user_token_and_image_url(self, user_id: str, token: str, image_url: str) -> None:
        self._db.user_db.update_user_token_and_image_url(user_id, token, image_url)
        self._cache.delete(get_user_key(user_id))

    def update_user_info(self, user_id: str, email: str, firstname: str, lastname: str, is_active: bool) -> None:
        self._db.user_db.update_user_info(
            user_id=user_id,
            email=email,
            firstname=firstname,
            lastname=lastname,
            is_active=is_active)
        self._cache.delete(get_user_key(user_id))
