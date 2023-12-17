import json

from databases.offices_db import OfficeDB
from poller.passport_website_query import PassportWebsiteQuery


def populate_office_db() -> None:
    pwc = PassportWebsiteQuery()
    office_db = OfficeDB()

    with open("../province.json", "r", encoding="utf-8") as f:
        options = json.load(f)
        provinces = map(lambda element: element["sigla"], options)

        for province in provinces:
            resp = pwc.query_province(province)

            for el in resp:
                office_db.insert_new_office(el)


if __name__ == "__main__":
    populate_office_db()
