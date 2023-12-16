import json
from datetime import datetime
from typing import Optional

import requests
from requests.structures import CaseInsensitiveDict


def _get_headers() -> CaseInsensitiveDict:
    headers : CaseInsensitiveDict = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Host"] = "passaportonline.poliziadistato.it"
    headers["Content-Type"] = "application/json"
    headers[
        "User-Agent"
    ] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/119.0"
    headers["Content-Length"] = "1319"
    headers["Origin"] = "https://passaportonline.poliziadistato.it"
    headers["Connection"] = "keep-alive"
    headers[
        "Cookie"
    ] = 'citrix_ns_id=AAE7b3p9ZTuyqAQAAAAAADsvHcVrHjWAsA_aO5TqWgFv8rY-EQJQcIS3qBmzYueyOw==EX59ZQ==-aGCYpkAmKuArR1EkqzYRPN0vcU=; citrix_ns_id_.poliziadistato.it_%2F_wat=AAAAAAXc9gYx5ZAhfGdeq7uiOY2fBIHRJEAW0lm0paG3eEzZHRpXguZaafmNU42Xj_uOaNK0dJrlXltsXhbEWw0t-KCE&; JSESSIONID="VoBdbQuWX1dQJGRjvJiqJSIg0Zetm9ucI2poKFgB.agpebeprd4-slave:agpebeprd4"; spid_domain_jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJodHRwczpcL1wvYXV0aC5wb2xpemlhZGlzdGF0by5pdCIsImlhdCI6MTcwMjY0NzE3NSwiZXhwIjoxNzAyNzMzNTc1LCJqdGkiOiI1Y2FmZGVmMi0yZGYxLTQxNmQtYjczOS1iOWNlOTEyN2EzNDYiLCJzdWIiOiI4ODIxMTYxOWRjYTJhMTNjYTM5MjZmMWZhZWFjZWUxYSIsImF1ZCI6ImRvbWFpblwvbHZsLTBcL3NsbyJ9.CPbAB5dECQew-OSgtuo6g0Jr-xDo0zedhN50XlSuexOmMkFI-La556Y1zQAB8fGWjWMf825HvkNsPouWFkcs4n31MQOpzVjNMCUoIk3OFRetsjSp9XXWJcMgdj3q4-mwmfBFHXrgALjCEcpQ4WUrqr6cmVMxX3EeHPGMbE7Kvv0nOqpSLfKBEOHH4Uc7wfTuh6W7JPdCa4oEZB-uQFZTl16R08RNqjKu4tNTxKJfbanlKc_rZef-Zq96cbrEKnlZd6JO-CYJ_tB2AlEzA7USqYJ5giTgYrpcYXVxssCBYThlWlG1QgrfNsk-SxVaZMsaZuLmyVGk_6BkJ2uKId9lTw'
    headers["X-CSRF-TOKEN"] = "0608a702-801c-4395-a0e3-24041be8e209"
    headers["Cache-Control"] = "no-cache"

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
    return f"{ts.day + 1}/{ts.month}/{ts.year}"


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
        self.query_url_agenda = ("https://passaportonline.poliziadistato.it/cittadino/n/rc/v1/utility/elenca-agenda"
                                 "-appuntamenti-sede-mese")
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
            print(f"Error, code {response.status_code}")
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
            + ',"dataRiferimento":"' + office["dataPrimaDisponibilitaResidenti"] + '","indietro":false}'
        )



        resp = requests.post(
            self.query_url_agenda, headers=self.query_header, data=office_request
        )

        print(json.loads(resp.content))


        if resp.status_code != 200:
            print(f"Error, code {resp.status_code}")
            return None

        availabilities = json.loads(resp.content)["elenco"]
        #availabilities = filter(
        #    lambda day: day["totAppuntamentiPresi"] < day["totAppuntamenti"],
        #    availabilities,
        #)

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
            print(f"Error, code {response.status_code}")
            return None

        return json.loads(response.content)["list"]
