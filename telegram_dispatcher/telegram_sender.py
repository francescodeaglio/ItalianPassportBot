import json
import urllib

import requests


class TelegramSender:
    def __init__(self):
        self.bot_token = "6655968162:AAFNVdebd2iuJ5qHXL3GY2g3fMGcz2HCn9w"

    def send_message(self, body: bytes) -> bool:
        entry = json.loads(body)
        print(entry)
        chat_id, message = entry["chat_id"], entry["content"]

        print(message)

        success = self._send_message(chat_id, message)

        if not success:
            return False
        return True

    def _send_message(self, chat_id, message) -> bool:
        url = (
            f"https://api.telegram.org/bot{self.bot_token}/sendMessage?chat_id="
            + str(chat_id)
            + ("&parse_mode=HTML" "&text=")
        )
        url = url + urllib.parse.quote_plus(message)

        if not requests.get(url).json()["ok"]:
            print("Error while sending the message", message, requests.get(url).json())
            return False
        return True
