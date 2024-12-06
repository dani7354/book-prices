from bookprices.shared.db.base import BaseDb
from bookprices.shared.model.api import ApiKey


class ApiKeyDb(BaseDb):
    def __init__(self, db_host: str, db_port: str, db_user: str, db_password: str, db_name: str):
        super().__init__(db_host, db_port, db_user, db_password, db_name)

    def get_api_key(self, api_name: str) -> ApiKey:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("SELECT Id, ApiName, ApiUser, ApiKey "
                         "FROM ApiKey "
                         "WHERE ApiName = %s;")
                cursor.execute(query, (api_name,))
                api_keys = []
                for row in cursor:
                    api_keys.append(ApiKey(
                        id=row["Id"],
                        api_name=row["ApiName"],
                        api_user=row["ApiUser"],
                        api_key=row["ApiKey"]))

                return api_keys[0] if len(api_keys) > 0 else None

    def add_api_key(self, api_key: ApiKey) -> None:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("INSERT INTO ApiKey "
                         "(ApiName, ApiUser, ApiKey) "
                         "VALUES (%s, %s, %s);")
                cursor.execute(query, (api_key.api_name, api_key.api_user, api_key.api_key))
                con.commit()

    def update_api_key(self, api_key: ApiKey) -> None:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("UPDATE ApiKey "
                         "SET ApiUser = %s, ApiKey = %s "
                         "WHERE Id = %s;")
                cursor.execute(query, (api_key.api_user, api_key.api_key, api_key.id))
                con.commit()
