import json
import logging
import urllib

import requests

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)
logging.getLogger("pika").propagate = False

class TelegramSender:
    def __init__(self):
        self.bot_token = "6655968162:AAFNVdebd2iuJ5qHXL3GY2g3fMGcz2HCn9w"

    def send_message(self, body: bytes) -> bool:
        entry = json.loads(body)

        chat_id, message = entry["chat_id"], entry["content"]
        logger.info(logging.INFO, "SENDING TO " + str(chat_id) + str(entry))

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
            logger.log(logging.ERROR, f"Error while sending the message {message}, {requests.get(url).json()}")
            return False
        return True
