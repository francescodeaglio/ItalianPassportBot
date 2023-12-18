import os

import mysql.connector


class PassportDB:
    def __init__(self):
        os.environ.setdefault("MYSQL_PORT", "3306")
        os.environ.setdefault("MYSQL_DB", "passport")

        self.connection = mysql.connector.connect(
            host=os.environ.get("MYSQL_HOST"),
            user=os.environ.get("MYSQL_USER"),
            password=os.environ.get("MYSQL_PASSWORD"),
            database=os.environ.get("MYSQL_DB"),
            port=os.environ.get("MYSQL_PORT"),
        )
