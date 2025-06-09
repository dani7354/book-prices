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

    def get_users(self, limit: int, offset: int) -> list[User]:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("SELECT Id, Email, FirstName, LastName, IsActive, GoogleApiToken, ImageUrl, Created, "
                         "Updated, AccessLevel "
                         "FROM User "
                         "ORDER BY Id "
                         "LIMIT %s "
                         "OFFSET %s")

                cursor.execute(query, (limit, offset))
                users = []
                for row in cursor:
                    users.append(User(row["Id"],
                                      row["Email"],
                                      row["FirstName"],
                                      row["LastName"],
                                      row["IsActive"],
                                      row["GoogleApiToken"],
                                      row["ImageUrl"],
                                      UserAccessLevel(row["AccessLevel"]),
                                      row["Created"],
                                      row["Updated"]))
                return users

    def create_user(self, new_user: User) -> None:
        with self.get_connection() as con:
            with con.cursor() as cursor:
                query = ("INSERT INTO User (Id, Email, FirstName, LastName, IsActive, GoogleApiToken, ImageUrl, "
                         "AccessLevel, Created, Updated) "
                         "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
                cursor.execute(query, (
                    new_user.id,
                    new_user.email,
                    new_user.firstname,
                    new_user.lastname,
                    new_user.is_active,
                    new_user.google_api_token,
                    new_user.image_url,
                    new_user.access_level.value,
                    new_user.created,
                    new_user.updated))
                con.commit()

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

    def delete_user(self, user_id: str):
        with self.get_connection() as con:
            with con.cursor() as cursor:
                query = "DELETE FROM User WHERE Id = %s"
                cursor.execute(query, (user_id,))
                con.commit()
