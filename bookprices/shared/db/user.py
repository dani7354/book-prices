from typing import Optional
from bookprices.shared.db.base import BaseDb
from bookprices.shared.model.user import User, UserAccessLevel


class UserDb(BaseDb):

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("SELECT Id, Email, FirstName, LastName, IsActive, GoogleApiToken, ImageUrl, Created, BookListId, "
                         "Updated, AccessLevel "
                         "FROM User "
                         "WHERE Id = %s")
                cursor.execute(query, (user_id,))
                user_dict = cursor.fetchone()
                if not user_dict:
                    return None

                return User(id=user_dict["Id"],
                            booklist_id=user_dict["BookListId"],
                            email=user_dict["Email"],
                            firstname=user_dict["FirstName"],
                            lastname=user_dict["LastName"],
                            is_active=user_dict["IsActive"],
                            google_api_token=user_dict["GoogleApiToken"],
                            image_url=user_dict["ImageUrl"],
                            access_level=UserAccessLevel(user_dict["AccessLevel"]),
                            created=user_dict["Created"],
                            updated=user_dict["Updated"])

    def get_users(self, limit: int, offset: int) -> list[User]:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("SELECT Id, Email, FirstName, LastName, IsActive, GoogleApiToken, ImageUrl, Created, BookListId, "
                         "Updated, AccessLevel "
                         "FROM User "
                         "ORDER BY Id "
                         "LIMIT %s "
                         "OFFSET %s")

                cursor.execute(query, (limit, offset))
                users = []
                for row in cursor:
                    users.append(User(id=row["Id"],
                                      booklist_id=row["BookListId"],
                                      email=row["Email"],
                                      firstname=row["FirstName"],
                                      lastname=row["LastName"],
                                      is_active=row["IsActive"],
                                      google_api_token=row["GoogleApiToken"],
                                      image_url=row["ImageUrl"],
                                      access_level=UserAccessLevel(row["AccessLevel"]),
                                      created=row["Created"],
                                      updated=row["Updated"]))
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

    def update_user_booklist(self, user_id: int, booklist_id: int) -> None:
        with self.get_connection() as con:
            with con.cursor() as cursor:
                query = ("UPDATE User "
                         "SET BookListId = %s "
                         "WHERE Id = %s")
                cursor.execute(query, (booklist_id, user_id))
                con.commit()
