import time

from databases.passport_db import PassportDB


class UserDB(PassportDB):
    def get_all_chat_ids_for_province(self, province: str) -> list[int]:
        cursor = self.connection.cursor()

        cursor.execute(f"SELECT chat_id FROM user WHERE province='{province}'")

        result = [entry[0] for entry in cursor.fetchall()]
        cursor.close()
        return result

    def get_all_active_provinces(self) -> list[str]:
        self.connection.commit()
        cursor = self.connection.cursor()

        cursor.execute("SELECT DISTINCT province FROM user")

        result = [entry[0] for entry in cursor.fetchall()]
        cursor.close()
        return result

    def get_all_active_provinces_user(self, chat_id) -> list[str]:
        self.connection.commit()
        cursor = self.connection.cursor()

        cursor.execute(f"SELECT province FROM user WHERE chat_id={chat_id}")

        result = [entry[0] for entry in cursor.fetchall()]
        cursor.close()
        return result

    def insert_new_user(self, chat_id: int, province: str) -> int:
        cursor = self.connection.cursor()
        join_time = int(time.time())
        cursor.execute(
            f"INSERT INTO user (chat_id, province, join_time) values ({chat_id},'{province}',{join_time}) "
        )
        self.connection.commit()
        cursor.close()

        return join_time

    def remove_user_province(self, user: int, province: str):
        cursor = self.connection.cursor()

        cursor.execute(
            f"DELETE FROM user WHERE province='{province}' and chat_id={user}"
        )

        self.connection.commit()
        cursor.close()

    def remove_user_all_provinces(self, chat_id: int) -> None:
        cursor = self.connection.cursor()

        print(chat_id)
        cursor.execute(f"DELETE FROM user WHERE chat_id={chat_id}")

        self.connection.commit()
        cursor.close()
