import json

from telegram import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from databases.user_db import UserDB

user_db = UserDB()


def get_intro_markup_and_text(user_id: int) -> tuple[InlineKeyboardMarkup, str]:
    already_subscribed = sorted(user_db.get_all_active_provinces_user(user_id))

    if len(already_subscribed) > 0:
        text_message = (
            "Al momento stai ricevendo gli aggiornamenti per le seguenti province: "
            + ", ".join(already_subscribed)
        ) + "\n\n"
        text_message += (
            "In questa schermata puoi smettere di ricevere le"
            " notifiche da una provincia o aggiungerne di nuove."
        )
    else:
        text_message = (
            "Premi sul bottone sottostante per"
            " ricevere gli aggiornamenti per la tua provincia."
        )

    keyboard = [
        InlineKeyboardButton("Aggiungi nuova provincia", callback_data="new")
    ] + [
        InlineKeyboardButton(
            f"Rimuovi provincia {prov}", callback_data=f"remove:{prov}"
        )
        for prov in already_subscribed
    ]

    if len(already_subscribed) > 1:
        # more than one subscribed province
        keyboard.append(
            InlineKeyboardButton(
                "Rimuovi tutte le province", callback_data="removeall"
            )
        )

    styled_keyboard = create_n_col_layout(keyboard, n=1)

    return InlineKeyboardMarkup(styled_keyboard), text_message


async def get_region(query: CallbackQuery) -> None:
    keyboard = [
        InlineKeyboardButton(entry, callback_data=f"region:{entry}")
        for entry in read_region()
    ]
    styled_keyboard = create_n_col_layout(keyboard, n=3)

    reply_markup = InlineKeyboardMarkup(styled_keyboard)
    await query.edit_message_text("Seleziona la regione:", reply_markup=reply_markup)


async def get_province(query: CallbackQuery, region: str) -> None:
    province = filter_region(region)
    keyboard = [
        InlineKeyboardButton(
            entry["nome"], callback_data=f"province:{entry['nome']}:{entry['sigla']}"
        )
        for entry in province
    ]

    styled_keyboard = create_n_col_layout(keyboard, n=3)

    reply_markup = InlineKeyboardMarkup(styled_keyboard)

    await query.edit_message_text("Seleziona la provincia:", reply_markup=reply_markup)


def filter_region(region: str) -> filter:
    with open("../province.json", "r", encoding="utf-8") as f:
        data = json.load(f)

        return filter(lambda entry: entry["regione"] == region, data)


def read_region() -> list:
    with open("../province.json", "r", encoding="utf-8") as f:
        data = json.load(f)

        return sorted(set(entry["regione"] for entry in data))


def create_n_col_layout(
    keyboard: list[InlineKeyboardButton], n: int
) -> list[list[InlineKeyboardButton]]:
    new_keyboard = []
    current_row: list[InlineKeyboardButton] = []
    counter = 0

    for element in keyboard:
        if counter % n == 0 and len(current_row) > 0:
            new_keyboard.append(current_row)
            current_row = []

        current_row.append(element)
        counter += 1

    if len(current_row) > 0:
        new_keyboard.append(current_row)

    return new_keyboard
