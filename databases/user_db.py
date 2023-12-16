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

        cursor.execute("SELECT DISTINCT province FROM user WHERE active=1")

        result = [entry[0] for entry in cursor.fetchall()]
        cursor.close()
        return result

    def get_all_active_provinces_user(self, chat_id) -> list[str]:
        self.connection.commit()
        cursor = self.connection.cursor()

        cursor.execute(
            f"SELECT province FROM user WHERE active=1 and chat_id={chat_id}"
        )

        result = [entry[0] for entry in cursor.fetchall()]
        cursor.close()
        return result

    def insert_new_user(self, chat_id: int, province: str) -> None:
        cursor = self.connection.cursor()
        cursor.execute(
            f"INSERT INTO user (chat_id, province, active) values ({chat_id},'{province}',1) "
        )
        self.connection.commit()
        cursor.close()

    def remove_user_province(self, user, province):
        cursor = self.connection.cursor()

        cursor.execute(
            f"DELETE FROM user WHERE province='{province}' and chat_id={user}"
        )

        self.connection.commit()
        cursor.close()
