import time

from databases.passport_db import PassportDB


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
            f"WHERE office_id={office_id} and available=1"
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
                    f"UPDATE availabilities"
                    f"SET available='0', ended_timestamp={end_timestamp} "
                    f"WHERE availability_id = {av_id}"
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
            else:
                print("Entry already stored")

        self.connection.commit()
        cursor.close()

        return new_availabilities
