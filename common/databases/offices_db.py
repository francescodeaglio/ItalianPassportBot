import json
import os

from common.databases.passport_db import PassportDB


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

    def get_all_provinces(self) -> list[str]:
        cursor = self.connection.cursor()
        cursor.execute("SELECT DISTINCT province_shortcut FROM office;")
        provinces = cursor.fetchall()
        cursor.close()

        return [el[0] for el in provinces]
