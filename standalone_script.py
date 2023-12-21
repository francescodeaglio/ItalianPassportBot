import json
import time
import urllib

import requests
from requests.structures import CaseInsensitiveDict


PROVINCE = "TO"
CHAT_ID_TELEGRAM = "" # FILL WITH YOUR CHAT ID
BOT_TOKEN = "6655968162:AAFNVdebd2iuJ5qHXL3GY2g3fMGcz2HCn9w"
URL_DISPONIBILITA = (
    "https://passaportonline.poliziadistato.it/cittadino/a/rc/v1/appuntamento/elenca-sede-prima"
    "-disponibilita"
)


def make_request_and_parse():
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Host"] = "passaportonline.poliziadistato.it"
    headers["Content-Type"] = "application/json"
    headers[
        "User-Agent"
    ] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/119.0"
    headers["Content-Length"] = "1319"
    headers["Origin"] = "https://passaportonline.poliziadistato.it"
    headers["Connection"] = "keep-alive"
    headers["Cache-Control"] = "no-cache"

    with open("./tokens/cookie_token", "r", encoding="utf-8") as f:
        headers["Cookie"] = f.read()

    with open("./tokens/xcsrf_token", "r", encoding="utf-8") as f:
        headers["X-CSRF-TOKEN"] = f.read()

    payload = (
        '{"comune":{"provinciaQuestura":"'
        + PROVINCE
        + '"},"pageInfo":{"maxResults":15},'
          '"sortInfo":{"sortList":[{"sortDirection":0,"sortProperty":"primaDisponibilitaResidente"}]}}'
    )

    resp = requests.post(URL_DISPONIBILITA, headers=headers, data=payload, timeout=60)

    return resp


def parse_resp(resp):
    sedi_disponibili = json.loads(resp.content)["list"]
    return [
        (
            sede["dataPrimaDisponibilitaResidenti"],
            sede["descrizione"],
            sede["orarioDisponibilita"],
        )
        for sede in sedi_disponibili
    ]


def send_message_telegram(message_text):
    url = (
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id="
        + CHAT_ID_TELEGRAM
        + "&parse_mode=MarkdownV2&text="
    )
    url = url + urllib.parse.quote_plus(message_text)
    if not requests.get(url).json()["ok"]:
        print("Error while sending the message", message_text, requests.get(url).json())


def main():
    # keep track of the available slots
    already_sent = set()

    while True:
        resp = make_request_and_parse()
        if resp.status_code != 200:
            send_message_telegram("Query Failed")
            print(resp, resp.status_code)
            break

        parsed = parse_resp(resp)

        print("Queried at " + str(time.time()))

        # send messages with new availabilities
        for element in parsed:
            if element[0] is not None and element not in already_sent:
                already_sent.add(element)
                data = "/".join(element[0].split("T")[0].split("-")[::-1])
                print(element)
                message = f"""
         Nuova disponibilità:
         *Data*: {data}
         *Sede*: {element[1].replace("-", " ").replace(".", "")}
         *Orario Disponibilita Prenotazione*: {element[2].replace(".", ":")}
                """
                send_message_telegram(message)

        # check booked slots
        for element in list(already_sent):
            if element not in parsed:
                already_sent.discard(element)
                data = "/".join(element[0].split("T")[0].split("-")[::-1])
                message = f"""
         *Non più disponibile*: {data} @ {element[1].replace("-", " ").replace(".", "")}
                """
                send_message_telegram(message)

        time.sleep(45)


if __name__ == "__main__":
    main()
