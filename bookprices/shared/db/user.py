from typing import Optional
from bookprices.shared.db.base import BaseDb
from bookprices.shared.model.user import User


class UserDb(BaseDb):

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("SELECT Id, Email, FirstName, LastName, IsActive, GoogleApiToken, Created, Updated "
                         "FROM User "
                         "WHERE Id = %s")
                cursor.execute(query, (user_id,))
                user_dict = cursor.fetchone()
                if not user_dict:
                    return None

                return User(user_dict["Id"],
                            user_dict["Email"],
                            user_dict["FirstName"],
                            user_dict["LastName"],
                            user_dict["IsActive"],
                            user_dict["GoogleApiToken"],
                            user_dict["Created"],
                            user_dict["Updated"])

    def get_user_by_email(self, email: str) -> Optional[User]:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("SELECT Id, Email, FirstName, LastName, IsActive, GoogleApiToken, Created, Updated "
                         "FROM User "
                         "WHERE Email = %s")
                cursor.execute(query, (email,))
                user_dict = cursor.fetchone()
                if not user_dict:
                    return None

                return User(user_dict["Id"],
                            user_dict["Email"],
                            user_dict["FirstName"],
                            user_dict["LastName"],
                            user_dict["IsActive"],
                            user_dict["GoogleApiToken"],
                            user_dict["Created"],
                            user_dict["Updated"])

    def update_user_token(self, email: str, token: str):
        with self.get_connection() as con:
            with con.cursor() as cursor:
                query = ("UPDATE User "
                         "SET GoogleApiToken = %s "
                         "WHERE Email = %s")
                cursor.execute(query, (token, email))
                con.commit()
