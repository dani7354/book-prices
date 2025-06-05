from typing import Optional
from bookprices.shared.db.base import BaseDb
from bookprices.shared.model.user import User, UserAccessLevel


class UserDb(BaseDb):

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("SELECT Id, Email, FirstName, LastName, IsActive, GoogleApiToken, ImageUrl, Created, "
                         "Updated, AccessLevel "
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
                            user_dict["ImageUrl"],
                            UserAccessLevel(user_dict["AccessLevel"]),
                            user_dict["Created"],
                            user_dict["Updated"])

    def update_user_token_and_image_url(self, user_id: str, token: str, image_url: str):
        with self.get_connection() as con:
            with con.cursor() as cursor:
                query = ("UPDATE User "
                         "SET GoogleApiToken = %s, ImageUrl = %s "
                         "WHERE Id = %s")
                cursor.execute(query, (token, image_url, user_id))
                con.commit()

    def update_user_info(
            self, user_id: str, email: str, firstname: str, lastname: str, access_level: int, is_active: bool):
        with self.get_connection() as con:
            with con.cursor() as cursor:
                query = ("UPDATE User "
                         "SET Email = %s, FirstName = %s, LastName = %s, IsActive = %s, AccessLevel = %s "
                         "WHERE Id = %s")
                cursor.execute(query, (email, firstname, lastname, is_active, access_level, user_id))
                con.commit()
