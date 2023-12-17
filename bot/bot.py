import logging

from configuration import get_intro_markup_and_text, get_province, get_region
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler,
                          ContextTypes, ConversationHandler)

from queues.queue_producer import QueueProducer

user_queue = QueueProducer("new_user")

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send message on `/start`."""

    if update.message is None or update.message.from_user is None:
        return 0

    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)

    reply_markup, text_message = get_intro_markup_and_text(
        update.message.from_user.id)
    await update.message.reply_text(f"{text_message}", reply_markup=reply_markup)
    # Tell ConversationHandler that we're in state `FIRST` now
    return 0


async def start_over(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.callback_query is None or update.callback_query.from_user is None:
        return 0

    query = update.callback_query
    await query.answer()
    reply_markup, text_message = get_intro_markup_and_text(
        update.callback_query.from_user.id
    )
    await query.edit_message_text(f"{text_message}", reply_markup=reply_markup)

    return 0


async def select_province(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.callback_query is None or update.callback_query.data is None:
        return 0

    query = update.callback_query
    await query.answer()

    selected_region = update.callback_query.data.split("region:")[1]
    await get_province(query, region=selected_region)
    return 0


async def select_region(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.callback_query is None:
        return 0

    query = update.callback_query
    await query.answer()

    await get_region(query)
    return 0


async def final_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.callback_query is None or update.callback_query.data is None:
        return 1

    query = update.callback_query
    await query.answer()

    data = update.callback_query.data.split("province:")[1]
    selected_province, shortcut = data.split(":")

    keyboard = [
        [
            InlineKeyboardButton(
                "Conferma Scelta", callback_data=f"confirm:{shortcut}"
            ),
            InlineKeyboardButton("Annulla e Ricomincia",
                                 callback_data="restart"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text=f"Hai selezionato la provincia di {selected_province} ({shortcut})",
        reply_markup=reply_markup,
    )
    return 1


async def end_and_persist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if (
        update.callback_query is None
        or update.callback_query.from_user is None
        or update.callback_query.data is None
    ):
        return ConversationHandler.END

    user, province = (
        update.callback_query.from_user.id,
        update.callback_query.data.split(":")[1],
    )

    user_queue.open_connection()
    user_queue.publish_new_message(
        {"chat_id": user, "province": province, "operation": "INSERT"}
    )
    user_queue.close_connection()

    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text=f"Scelta salvata: Aggiunta Provincia {province}")

    return ConversationHandler.END


async def remove_province(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if (
        update.callback_query is None
        or update.callback_query.from_user is None
        or update.callback_query.data is None
    ):
        return ConversationHandler.END

    user, province = (
        update.callback_query.from_user.id,
        update.callback_query.data.split(":")[1],
    )
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text=f"Scelta salvata: Rimossa provincia {province}")

    user_queue.open_connection()
    user_queue.publish_new_message(
        {"chat_id": user, "province": province, "operation": "REMOVE"}
    )
    user_queue.close_connection()

    return ConversationHandler.END


async def remove_all_provinces(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    if (
        update.callback_query is None
        or update.callback_query.from_user is None
        or update.callback_query.data is None
    ):
        return ConversationHandler.END

    user = update.callback_query.from_user.id

    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text=f"Scelta salvata: Rimosse tutte le province")

    user_queue.open_connection()
    user_queue.publish_new_message(
        {"chat_id": user, "province": None, "operation": "REMOVE ALL"}
    )
    user_queue.close_connection()

    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = (
        Application.builder()
        .token("6655968162:AAFNVdebd2iuJ5qHXL3GY2g3fMGcz2HCn9w")
        .build()
    )

    # Setup conversation handler with the states FIRST and SECOND
    # Use the pattern parameter to pass CallbackQueries with specific
    # data pattern to the corresponding handlers.
    # ^ means "start of line/string"
    # $ means "end of line/string"
    # So ^ABC$ will only allow 'ABC'
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            0: [
                CallbackQueryHandler(select_province, pattern="^region"),
                CallbackQueryHandler(select_region, pattern="^new$"),
                CallbackQueryHandler(final_confirmation, pattern="^province"),
                CallbackQueryHandler(remove_province, pattern="^remove:"),
                CallbackQueryHandler(remove_all_provinces,
                                     pattern="^removeall$"),
            ],
            1: [
                CallbackQueryHandler(start_over, pattern="^restart$"),
                CallbackQueryHandler(end_and_persist, pattern="^confirm"),
            ],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    # Add ConversationHandler to application that will be used for handling updates
    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
