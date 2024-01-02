from abstract_user_handler import AbstractUserHandler


class TelegramUserHandler(AbstractUserHandler):
    def __init__(self):
        super().__init__()
        self.channel = "TELEGRAM"
