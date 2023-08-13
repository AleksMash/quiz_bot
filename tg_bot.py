from datetime import datetime

from environs import Env
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, CallbackContext,
                          ConversationHandler, CallbackQueryHandler)
# lib for fuzzy comparing answer vs question
from fuzzywuzzy import fuzz

import db
import tg_bot_settings as bs


env = Env()
env.read_env()


def process_input_data(user_id, user_data, update: Update):
    if user_data[bs.CURRENT_STAGE] == bs.ANSWER_QUESTION:
        right_answer = user_data[bs.CURRENT_QUESTION]['a']
        user_answer = user_data[bs.INPUT_DATA][0]
        # Вес 70 применен эмпирически
        if fuzz.WRatio(user_answer, right_answer)>=70:
            update.message.reply_text("Правильно! Поздравляю! Для следующего вопроса нажми \"Новый вопрос\"",
                                    reply_markup=bs.KB_START)
            return bs.SELECT_ACTION
        else:
            update.message.reply_text("Ответ неверный. Хотите попробовать ответить еще раз?", reply_markup=bs.KB_YES_NO)
            return bs.YES_OR_NO_REPEAT


def start(update: Update, context: CallbackContext):
    update.message.reply_text("Выбери действие", reply_markup=bs.KB_START)
    return bs.SELECT_ACTION


def new_question(update: Update, context: CallbackContext):
    question = db.fetch_random_question()
    context.user_data[bs.CURRENT_STAGE] = bs.ANSWER_QUESTION
    context.user_data[bs.NEXT_STAGE] = bs.SELECT_ACTION
    context.user_data[bs.CURRENT_STEP] = 0
    context.user_data[bs.CURRENT_QUESTION] = question
    context.user_data[bs.LAST_STEP] = len(bs.INPUT_STEPS[bs.ANSWER_QUESTION])-1
    context.user_data[bs.INPUT_DATA] = []
    update.message.reply_text(question['q'])
    update.message.reply_text(bs.INPUT_STEPS[bs.ANSWER_QUESTION][0][0], reply_markup=bs.CANCEL_MARKUP)
    return bs.ANSWER_QUESTION


def repeat_question(update: Update, context: CallbackContext):
    update.message.reply_text('Повторяю вопрос: \n\n'+ context.user_data[bs.CURRENT_QUESTION]['q'],
                              reply_markup=bs.KB_START)
    update.message.reply_text(bs.INPUT_STEPS[bs.ANSWER_QUESTION][0][0], reply_markup=bs.CANCEL_MARKUP)
    return bs.ANSWER_QUESTION


def give_up(update: Update, context: CallbackContext):
    update.message.reply_text('Правильный ответ таков:\n\n' + context.user_data[bs.CURRENT_QUESTION]['a'])
    return bs.SELECT_ACTION


def get_user_text(update: Update, context: CallbackContext):
    current_step = context.user_data[bs.CURRENT_STEP]
    current_stage = context.user_data[bs.CURRENT_STAGE]
    checker = bs.INPUT_STEPS[current_stage][current_step][1]
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
        next_msg = bs.INPUT_STEPS[current_stage][current_step][0]
        update.message.reply_text(next_msg, reply_markup=bs.CANCEL_MARKUP)
        return context.user_data[bs.CURRENT_STAGE]

    return process_input_data(update.message.from_user.id, context.user_data, update)


def cancel_input(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    context.user_data.clear
    query.message.reply_text('Ввод данных отменен', reply_markup=bs.KB_START)
    return bs.SELECT_ACTION


def main():
    updater = Updater(env.str('TG_BOT_TOKEN'))
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            bs.SELECT_ACTION:[
                MessageHandler(filters=Filters.text([bs.NEW_QUESTION]), callback=new_question),
            ],
            bs.ANSWER_QUESTION:[
                MessageHandler(filters=Filters.text([bs.GIVE_UP]), callback=give_up),
                MessageHandler(filters=None, callback=get_user_text),
                CallbackQueryHandler(cancel_input, pattern=bs.CANCEL_INPUT)
            ],
            bs.YES_OR_NO_REPEAT:[
                MessageHandler(filters=Filters.text([bs.NO]), callback=start),
                MessageHandler(filters=Filters.text([bs.YES]), callback=repeat_question)
            ]
        },
        fallbacks=[CommandHandler('start', start)],
        per_user=True
    )

    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
