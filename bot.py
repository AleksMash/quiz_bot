from datetime import datetime
from environs import Env


from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, CallbackContext,
                          ConversationHandler, CallbackQueryHandler)

import db
import bot_settings as bs


env = Env()
env.read_env()


def save_input_data(user_id, user_data):
    if user_data[bs.CURRENT_BUTTON] == bs.NEW_QUESTION:
        print('user_id: ', user_id)
        db.save_question(user_id, user_data[bs.INPUT_DATA][0])


def start(update: Update, context: CallbackContext):
    update.message.reply_text("Привет! Выбери действие", reply_markup=bs.COMMON_REPLY_BUTTONS)
    return bs.SELECT_ACTION

def test(update: Update, context: CallbackContext):
    update.message.reply_text(f"В БД сохранено:\n\n {db.fetch_question(update.message.from_user.id)}")
    return bs.SELECT_ACTION


def new_question(update: Update, context: CallbackContext):
    context.user_data[bs.CURRENT_BUTTON] = bs.NEW_QUESTION
    context.user_data[bs.CURRENT_STAGE] = bs.ANY_TEXT_INPUT
    context.user_data[bs.NEXT_STAGE] = bs.SELECT_ACTION
    context.user_data[bs.CURRENT_STEP] = 0
    context.user_data[bs.LAST_STEP] = len(bs.INPUT_STEPS[bs.NEW_QUESTION])-1
    context.user_data[bs.INPUT_DATA] = []
    update.message.reply_text(bs.INPUT_STEPS[bs.NEW_QUESTION][0][0], reply_markup=bs.CANCEL_MARKUP)
    return bs.ANY_TEXT_INPUT


def get_user_text(update: Update, context: CallbackContext):
    current_step = context.user_data[bs.CURRENT_STEP]
    current_button = context.user_data[bs.CURRENT_BUTTON]
    checker = bs.INPUT_STEPS[current_button][current_step][1]
    if not checker is str:
        try:
            input_checked = checker(update.message.text)
        except (ValueError, TypeError):
            update.message.reply_text('Вы ввели неверное значение./n', reply_markup=bs.CANCEL_MARKUP)
            return context.user_data[bs.CURRENT_STAGE]
    else:
        input_checked = update.message.text

    context.user_data[bs.INPUT_DATA].append(input_checked)

    if not current_step == context.user_data[bs.LAST_STEP]:
        current_step += 1
        context.user_data[bs.CURRENT_STEP] = current_step
        next_msg = bs.INPUT_STEPS[current_button[current_step][0]]
        update.message.reply_text(next_msg, reply_markup=bs.CANCEL_MARKUP)
        return context.user_data[bs.CURRENT_STAGE]

    save_input_data(update.message.from_user.id, context.user_data)
    next_stage = context.user_data[bs.NEXT_STAGE]
    context.user_data.clear
    return next_stage


def about_bot(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.message.reply_text('Информация о боте')


def cancel_input(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    context.user_data.clear
    # context.user_data[bs.CURRENT_BUTTON] = None
    # context.user_data[bs.INPUT_STEP] = None
    # context.user_data[bs.INPUT_DATA] = None
    query.message.reply_text('Ввод данных отменен')
    return bs.SELECT_ACTION


def main():
    updater = Updater(env.str('TG_BOT_TOKEN'))
    dispatcher = updater.dispatcher
    # cancel_button_handler = CallbackQueryHandler(cancel_input, pattern=bs.CANCEL_INPUT)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            bs.SELECT_ACTION:[
                MessageHandler(filters=Filters.text([bs.NEW_QUESTION]), callback=new_question),
            ],
            bs.ANY_TEXT_INPUT:[
                MessageHandler(filters=None, callback=get_user_text),
                CallbackQueryHandler(cancel_input, pattern=bs.CANCEL_INPUT)
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
