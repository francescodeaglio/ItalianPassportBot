import time

from common.databases.passport_db import PassportDB


def check_existing_availability(cursor, office_id, day, hour):
    cursor.execute(
        f"SELECT COUNT(*) "
        f"FROM availabilities "
        f'WHERE office_id={office_id} and day="{day}" and hour="{hour}" and available=1'
    )
    r = cursor.fetchall()
    return int(r[0][0]) > 0


class AvailabilitiesDB(PassportDB):
    def set_no_longer_available_entries(self, query_entry):
        office_id = query_entry["office_id"]

        cursor = self.connection.cursor()
        cursor.execute(
            f"SELECT availability_id, day, hour "
            f"FROM availabilities "
            f"WHERE office_id={office_id} and available='1'"
        )
        open_availabilities = cursor.fetchall()

        for avail in open_availabilities:
            av_id, day, hour = avail

            found = False
            for el in query_entry["availabilities"]:
                if el["hour"] == hour and el["day"] == day:
                    found = True
                    break

            if not found:
                end_timestamp = int(time.time())
                cursor.execute(
                    f"""UPDATE availabilities
                    SET available='0', ended_timestamp={end_timestamp}
                    WHERE availability_id = {av_id}"""
                )

        self.connection.commit()
        cursor.close()

    def insert_new_availability(self, query_entry: dict) -> list:
        cursor = self.connection.cursor()

        office_id = query_entry["office_id"]
        discovered_timestamp = int(time.time())

        new_availabilities = []

        for availability in query_entry["availabilities"]:
            day = availability["day"]
            hour = availability["hour"]
            slots = availability["slots"]

            if not check_existing_availability(cursor, office_id, day, hour):
                cursor.execute(
                    f"INSERT INTO availabilities "
                    f"(office_id, day, hour, slots, discovered_timestamp, available) "
                    f'VALUES({office_id}, "{day}", "{hour}", {slots}, {discovered_timestamp}, 1);'
                )
                new_availabilities.append(availability)

        self.connection.commit()
        cursor.close()

        return new_availabilities

    def get_slots_available_before(self, province, join_time) -> list[dict]:
        query = f"""SELECT o.name, o.address, o.city, a.day, a.hour, a.slots 
        FROM availabilities AS a, office AS o 
        WHERE a.office_id=o.office_id and a.discovered_timestamp < {join_time} and a.available='1' and o.province_shortcut='{province}' 
        ORDER BY o.name, a.day, a.hour;"""

        cursor = self.connection.cursor()

        cursor.execute(query)

        return [
            {
                "name": el[0],
                "address": el[1],
                "city": el[2],
                "day": el[3],
                "hour": el[4],
                "slots": el[5],
            }
            for el in cursor.fetchall()
        ]

    def update_slots(self, to_be_updated):
        cursor = self.connection.cursor()
        for entry in to_be_updated:
            id = entry["availability_id"]
            new_slots = entry["slots"]
            cursor.execute(
                f"""
            UPDATE availabilities
            SET slots={new_slots}
            WHERE availability_id={id}
            """
            )

        self.connection.commit()
        cursor.close()

    def set_no_longer_available(self, to_be_set_inactive):
        cursor = self.connection.cursor()
        for id in to_be_set_inactive:
            end_timestamp = int(time.time())

            cursor.execute(
                f"""
                    UPDATE availabilities
                    SET slots=0, available='0', ended_timestamp={end_timestamp}
                    WHERE availability_id={id}
                    """
            )

        self.connection.commit()
        cursor.close()

    def get_active_availabilities(self, province):
        cursor = self.connection.cursor()

        cursor.execute(
            f"""
            SELECT availability_id, a.office_id, day, hour, slots 
            FROM availabilities as a, office as o
            WHERE o.office_id = a.office_id and available='1' and province_shortcut='{province}';
            """
        )
        result = cursor.fetchall()
        cursor.close()
        return result
