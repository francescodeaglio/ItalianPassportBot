def day_builder(day_info: dict) -> str:
    day: str = day_info["day"]
    hour = day_info["hour"]  # .replace(".", "\\.")
    slots = day_info["slots"]

    return f"   {day} ore {hour} Slot{'s' if slots > 1 else ''} disponibili: {slots}"


def get_text_entry(entries):
    first_entry = entries[0]
    name = first_entry["name"]
    address = first_entry["address"] + " " + first_entry["city"]
    day_availabilities = "\n".join(map(lambda d: day_builder(d), entries))

    return f"Sede: {name}\nIndirizzo: {address}\n{day_availabilities}\n\n"


def create_summary_message(entries):
    processed_offices = set()

    return_text = "Disponibilità: \n"
    for entry in entries:
        if entry["name"] not in processed_offices:
            processed_offices.add(entry["name"])
            text = get_text_entry(
                list(filter(lambda d: d["name"] == entry["name"], entries))
            )
            return_text += text

    return return_text
