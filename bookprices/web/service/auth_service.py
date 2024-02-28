from typing import Optional

import flask
import flask_login
from flask_caching import Cache

from bookprices.shared.db. database import Database
from bookprices.web.cache.key_generator import get_user_key


class User(flask_login.UserMixin):
    pass


class AuthService:
    def __init__(self, db: Database, cache: Cache):
        self.db = db
        self.cache = cache

    def get_user(self, user_id: str) -> Optional[User]:
        if not (user := self.cache.get(get_user_key(user_id))):
            user = self.db.user_db.get_user_by_id(user_id)
            if user:
                self.cache.set(get_user_key(user_id), user)

        return user


