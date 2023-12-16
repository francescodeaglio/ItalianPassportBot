import json
from databases.passport_db import PassportDB
from poller.passport_website_query import PassportWebsiteQuery


def populate_office_db() -> None:
    pwc = PassportWebsiteQuery()
    office_db = OfficeDB()

    with open("province.json", "r", encoding="utf-8") as f:
        options = json.load(f)
        provinces = map(lambda element: element["sigla"], options)

        for province in provinces:
            resp = pwc.query_province(province)

            for el in resp:
                office_db.insert_new_office(el)


class OfficeDB(PassportDB):

    def insert_new_office(self, office_entry: dict) -> None:
        print(office_entry)
        office_id = office_entry["id"]
        cap = office_entry["cap"]
        city = office_entry["citta"]
        code = office_entry["codice"]
        name = office_entry["descrizione"].replace('"', "")
        address = office_entry["indirizzo"]
        province = office_entry["provincia"]
        av_time = office_entry["orarioDisponibilita"]

        cursor = self.connection.cursor()
        cursor.execute(
            f"""INSERT INTO office (office_id, cap, city, code, name, address, province, time) 
            VALUES ({office_id},"{cap}","{city}", "{code}", 
            "{name}", "{address}", "{province}", "{av_time}") """
        )
        self.connection.commit()
        cursor.close()
