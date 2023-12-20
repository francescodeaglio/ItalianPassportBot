import json
import logging
from datetime import datetime, timedelta
from typing import Optional

import requests
from requests.structures import CaseInsensitiveDict


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)
logging.getLogger("pika").propagate = False


def _get_headers() -> CaseInsensitiveDict:
    headers: CaseInsensitiveDict = CaseInsensitiveDict()
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

    with open("cookie_token", "r") as f:
        headers["Cookie"] = f.read()

    with open("xcsrf_token", "r") as f:
        headers["X-CSRF-TOKEN"] = f.read()

    return headers


def parse_response(
    available_offices: list[dict],
) -> list[Optional[tuple[str, str, str]]]:
    return [
        (
            office["dataPrimaDisponibilitaResidenti"],
            office["descrizione"],
            office["orarioDisponibilita"],
        )
        for office in available_offices
    ]


def parse_day(day):
    ts = datetime.utcfromtimestamp(day / 1000)
    ts = ts + timedelta(hours=1)  # use correct timezone
    return f"{ts.day}/{ts.month}/{ts.year}"


def get_available_offices(response_offices: dict) -> list[dict]:
    return list(
        filter(
            lambda office: office["dataPrimaDisponibilitaResidenti"] is not None,
            response_offices,
        )
    )


class PassportWebsiteQuery:
    def __init__(self):
        self.query_url_availabilities = (
            "https://passaportonline.poliziadistato.it/cittadino/a/rc/v1/appuntamento"
            "/elenca-sede-prima-disponibilita"
        )
        self.query_url_agenda = (
            "https://passaportonline.poliziadistato.it/cittadino/n/rc/v1/utility/elenca-agenda"
            "-appuntamenti-sede-mese"
        )
        self.query_header = _get_headers()

    def get_availability_province(self, province: str) -> Optional[list[dict]]:
        payload = (
            '{"comune":{"provinciaQuestura":"'
            + province
            + (
                '"},'
                '"pageInfo":{"maxResults":15},'
                '"sortInfo":{"sortList":[{"sortDirection":0,'
                '"sortProperty":"primaDisponibilitaResidente"}]}}'
            )
        )

        response = requests.post(
            self.query_url_availabilities, headers=self.query_header, data=payload
        )

        if response.status_code != 200:
            logger.log(logging.ERROR, f"Error, code {response.status_code}")
            return None

        response_offices = json.loads(response.content)["list"]

        available_offices = get_available_offices(response_offices)

        return_list = []
        for office in available_offices:
            return_list.append(
                {
                    "date": office["dataPrimaDisponibilitaResidenti"],
                    "office_name": office["descrizione"],
                    "office_id": office["id"],
                    "address": office["indirizzo"],
                    "city": office["comune"],
                    "hour": office["orarioDisponibilita"],
                    "availabilities": self.process_available_office(office),
                }
            )

        return return_list

    def process_available_office(self, office: dict) -> Optional[list]:
        office_request = (
            '{"sede":'
            + json.dumps(office)
            + ',"dataRiferimento":"'
            + office["dataPrimaDisponibilitaResidenti"]
            + '","indietro":false}'
        )

        resp = requests.post(
            self.query_url_agenda, headers=self.query_header, data=office_request
        )

        if resp.status_code != 200:
            logger.log(logging.ERROR, f"Error, code {response.status_code}")
            return None

        availabilities = json.loads(resp.content)["elenco"]
        # availabilities = filter(
        #    lambda day: day["totAppuntamentiPresi"] < day["totAppuntamenti"],
        #    availabilities,
        # )

        parsed = [
            {
                "day": parse_day(day["giorno"]),
                "hour": day["ora"],
                "slots": day["totAppuntamenti"],
            }
            for day in availabilities
        ]

        return parsed

    def query_province(self, province: str) -> Optional[list]:
        payload = (
            '{"comune":{"provinciaQuestura":"'
            + province
            + (
                '"},'
                '"pageInfo":{"maxResults":30},'
                '"sortInfo":{"sortList":[{"sortDirection":0,'
                '"sortProperty":"primaDisponibilitaResidente"}]}}'
            )
        )

        response = requests.post(
            self.query_url_availabilities, headers=self.query_header, data=payload
        )

        if response.status_code != 200:
            logger.log(logging.ERROR, f"Error, code {response.status_code}")
            return None

        return json.loads(response.content)["list"]
