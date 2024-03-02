import flask_login
from datetime import datetime
from flask_caching import Cache
from typing import Optional
from bookprices.shared.db. database import Database
from bookprices.shared.model.user import User
from bookprices.web.cache.key_generator import get_user_key


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

    def get_id(self) -> str:
        return self.id


class AuthService:
    def __init__(self, db: Database, cache: Cache):
        self.db = db
        self.cache = cache

    def get_user(self, user_id: str) -> Optional[WebUser]:
        if not (user := self.cache.get(get_user_key(user_id))):
            user = self.db.user_db.get_user_by_id(user_id)
            if user:
                self.cache.set(get_user_key(user_id), user)
        return WebUser(user) if user else None
