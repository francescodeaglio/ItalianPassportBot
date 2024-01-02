def _message_builder(
    query_entry: dict, new_availabilities: list, scheduled: bool
) -> str:
    print("\tSENDING", query_entry)

    date = "/".join(query_entry["date"].split("T")[0].split("-")[::-1])
    day_availabilities = "\n".join(map(day_builder, new_availabilities))

    if not scheduled:
        header = "Nuova disponibilità:"
    else:
        start_hour = query_entry["hour"]
        header = f"Nuova disponibilità alle ore {start_hour}:"

    return f"""
{header}
Prima Data: {date}
Disponibilità:
{day_availabilities}
Sede: {query_entry["office_name"]}
Indirizzo: {query_entry["address"]} {query_entry["city"]}
    """


def day_builder(day_info: dict) -> str:
    day: str = day_info["day"]
    hour = day_info["hour"]  # .replace(".", "\\.")
    slots = day_info["slots"]

    return f"   {day} ore {hour} Slot disponibili: {slots}"
