import urllib

import requests

BOT_TOKEN = "6655968162:AAFNVdebd2iuJ5qHXL3GY2g3fMGcz2HCn9w"


def telegram_message_sender(chat_id: int, message: str) -> None:
    url = (
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id="
        + str(chat_id)
        + ("&parse_mode=MarkdownV2" "&text=")
    )
    url = url + urllib.parse.quote_plus(message)
    if not requests.get(url).json()["ok"]:
        print("Error while sending the message",
              message, requests.get(url).json())


def telegram_message_builder(query_entry: dict) -> str:
    date = "/".join(query_entry["date"].split("T")[0].split("-")[::-1])
    day_availabilities = "\n".join(
        map(lambda d: day_builder(d), query_entry["availabilities"])
    )

    return f"""
Nuova disponibilità:
*Prima Data*: {date}
*Disponibilità*:
{day_availabilities}
*Sede*: {query_entry["office_name"].replace("-", " ").replace(".", "")}
*Indirizzo*: {query_entry["address"].replace("-", " ").replace(".", "")} {query_entry["city"]}
    """


def day_builder(day_info: dict) -> str:
    day: str = day_info["day"]
    hour = day_info["hour"].replace(".", "\\.")
    slots = day_info["slots"]

    return f"   {day} ore {hour} Slots disponibili: {slots}"
