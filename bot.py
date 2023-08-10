from datetime import datetime
from environs import Env


from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, CallbackContext,
                          ConversationHandler, CallbackQueryHandler)

import db
import bot_settings as bs


env = Env()
env.read_env()


def plug_function(update: Update, context: CallbackContext):
    pass


def start(update: Update, context: CallbackContext):
    update.message.reply_text("Привет! Выбери действие", reply_markup=bs.COMMON_REPLY_BUTTONS)
    return bs.WAIT_FOR_BUTTONS

def answer(update: Update, context: CallbackContext):
    update.message.reply_text("Ты нажал кнопку!", reply_markup=bs.COMMON_REPLY_BUTTONS)
    return bs.WAIT_FOR_BUTTONS


def about_bot(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.message.reply_text('Информация о боте')


def cancel_input(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    context.user_data[bs.CURRENT_STATE] = None
    context.user_data[bs.INPUT_STEP] = None
    context.user_data[bs.INPUT_DATA] = None
    query.message.reply_text('Действие отменено. \n /Start - для перехода в главное меню')
    return bs.WAIT_FOR_BUTTONS


def main():
    updater = Updater(env.str('TG_BOT_TOKEN'))
    dispatcher = updater.dispatcher
    # cancel_button_handler = CallbackQueryHandler(cancel_input, pattern=bs.CANCEL_INPUT)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            bs.WAIT_FOR_BUTTONS: [
                MessageHandler(filters=None, callback=answer)
            ]
        },
        fallbacks=[CommandHandler('start', start)],
        per_user=True
    )

    # Add ConversationHandler to dispatcher that will be used for handling updates
    dispatcher.add_handler(conv_handler)
    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
