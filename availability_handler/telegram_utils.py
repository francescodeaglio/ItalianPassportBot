def telegram_message_builder(query_entry: dict, new_availabilities: list) -> str:
    date = "/".join(query_entry["date"].split("T")[0].split("-")[::-1])
    day_availabilities = "\n".join(map(lambda d: day_builder(d), new_availabilities))
    return f"""
Nuova disponibilità:
Prima Data: {date}
Disponibilità:
{day_availabilities}
Sede: {query_entry["office_name"]}
Indirizzo: {query_entry["address"]} {query_entry["city"]}
    """


def day_builder(day_info: dict) -> str:
    day: str = day_info["day"]
    hour = day_info["hour"].replace(".", "\\.")
    slots = day_info["slots"]

    return f"   {day} ore {hour} Slot{'s' if slots> 1 else ''} disponibili: {slots}"
