import json
from databases.passport_db import PassportDB
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


class OfficeDB(PassportDB):
    def __init__(self):
        super().__init__()
        self.province_mapping = {}
        with open("../province.json") as f:
            provinces = json.load(f)
            for entry in provinces:
                self.province_mapping[entry["nome"].upper()] = entry["sigla"]

    def insert_new_office(self, office_entry: dict) -> None:
        office_id = office_entry["id"]
        cap = office_entry["cap"]
        city = office_entry["comune"]
        code = office_entry["codice"]
        name = office_entry["descrizione"].replace('"', "")
        address = office_entry["indirizzo"]
        province = office_entry["provincia"]
        av_time = office_entry["orarioDisponibilita"]
        shortcut = self.province_mapping.get(province, "ZZ")

        if province == "ZZ":
            print(city, province, shortcut)
            return

        cursor = self.connection.cursor()
        cursor.execute(
            f"""INSERT INTO office (office_id, cap, city, code, name, address, province, province_shortcut, time) 
            VALUES ({office_id},"{cap}","{city}", "{code}", 
            "{name}", "{address}", "{province}", "{shortcut}", "{av_time}") """
        )
        self.connection.commit()
        cursor.close()


if __name__ == "__main__":
    populate_office_db()
