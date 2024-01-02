import time

from common.databases.passport_db import PassportDB


class UserDB(PassportDB):
    def get_all_chat_ids_for_province(self, province: str) -> list[int]:
        self.connection.commit()
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

    def get_all_active_provinces_user(self, chat_id: int, channel: str) -> list[str]:
        self.connection.commit()
        cursor = self.connection.cursor()

        cursor.execute(f"SELECT province FROM user WHERE chat_id={chat_id} and channel='{channel}'")

        result = [entry[0] for entry in cursor.fetchall()]
        cursor.close()
        return result

    def insert_new_user(self, chat_id: int, channel: str, province: str) -> int:
        cursor = self.connection.cursor()
        join_time = int(time.time())
        cursor.execute(
            f"INSERT INTO user (chat_id, channel, province, join_time) values ({chat_id},'{channel}','{province}',{join_time}) "
        )
        self.connection.commit()
        cursor.close()

        return join_time

    def remove_user_province(self, user_id: int, channel: str, province: str):
        cursor = self.connection.cursor()

        cursor.execute(
            f"DELETE FROM user WHERE province='{province}' and chat_id={user_id} and channel='{channel}'"
        )

        self.connection.commit()
        cursor.close()

    def remove_user_all_provinces(self, chat_id: int, channel:str) -> None:
        cursor = self.connection.cursor()

        print(chat_id)
        cursor.execute(f"DELETE FROM user WHERE chat_id={chat_id} and channel='{channel}'")

        self.connection.commit()
        cursor.close()

    def at_lest_one_user_province(self, province):
        cursor = self.connection.cursor()

        cursor.execute(
            f"SELECT count(*) FROM user WHERE province='{province}'")
        result = cursor.fetchall()
        self.connection.commit()
        cursor.close()

        return result[0][0] > 0
