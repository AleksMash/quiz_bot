import os, json, random

import redis

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, CallbackContext,
                          ConversationHandler, CallbackQueryHandler, Dispatcher)

# lib for fuzzy comparing answer vs question
from fuzzywuzzy import fuzz


# data elements for saving in callback context
INPUT_DATA = 1
CURRENT_STAGE = 2

# conversation stages
SELECT_ACTION = 1       # waiting for user clicks any of replymarkup button
ANSWER_QUESTION = 2     # waiting for user answer
YES_OR_NO_REPEAT = 3    # wait for user choice to continue or not answering

# reply buttons
NEW_QUESTION = 'Новый вопрос'
GIVE_UP = 'Сдаться'
RATE = 'Мой счет'
YES = 'Да'
NO = 'Нет'

#callback buttons data
CANCEL_INPUT = 'cancel'

# Cancel button for cancelling input
CANCEL_MARKUP = InlineKeyboardMarkup.from_button(InlineKeyboardButton('Отмена', callback_data=CANCEL_INPUT))

# replymarkups
KEYBOARD_START = ReplyKeyboardMarkup(
    [[NEW_QUESTION, GIVE_UP]]
)

KEYBOARD_YES_NO = ReplyKeyboardMarkup(
    [[YES, NO]]
)


def process_user_answer(update: Update, context: CallbackContext):
    if context.user_data[CURRENT_STAGE] == ANSWER_QUESTION:
        right_answer = context.bot_data['redis'].get(f'{update.message.from_user.id}_a')
        # Вес 70 применен эмпирически
        if fuzz.WRatio(update.message.text, right_answer)>=70:
            update.message.reply_text("Правильно! Поздравляю! Для следующего вопроса нажми \"Новый вопрос\"",
                                      reply_markup=KEYBOARD_START)
            return SELECT_ACTION
        else:
            update.message.reply_text("Ответ неверный. Хотите попробовать ответить еще раз?", reply_markup=KEYBOARD_YES_NO)
            return YES_OR_NO_REPEAT


def start(update: Update, context: CallbackContext):
    update.message.reply_text("Выбери действие", reply_markup=KEYBOARD_START)
    return SELECT_ACTION


def new_question(update: Update, context: CallbackContext):
    question = random.choice(context.bot_data['questions'])
    context.user_data[CURRENT_STAGE] = ANSWER_QUESTION
    update.message.reply_text(question[0])
    update.message.reply_text('Введите  ответ', reply_markup=CANCEL_MARKUP)
    context.bot_data['redis'].set(f'{update.message.from_user.id}_q', question[0])
    context.bot_data['redis'].set(f'{update.message.from_user.id}_a', question[1])
    return ANSWER_QUESTION


def repeat_question(update: Update, context: CallbackContext):
    question = context.bot_data['redis'].get(f'{update.message.from_user.id}_q').decode('UTF-8')
    update.message.reply_text(f'Повторяю вопрос:\n\n{question}', reply_markup=KEYBOARD_START)
    update.message.reply_text('Введите  ответ', reply_markup=CANCEL_MARKUP)
    return ANSWER_QUESTION


def give_up(update: Update, context: CallbackContext):
    right_answer = context.bot_data['redis'].get(f'{update.message.from_user.id}_a').decode('UTF-8')
    update.message.reply_text(f'Правильный ответ таков:\n\n{right_answer}')
    return SELECT_ACTION


def cancel_input(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    context.user_data.clear
    query.message.reply_text('Ввод данных отменен', reply_markup=KEYBOARD_START)
    return SELECT_ACTION


def main():
    load_dotenv()
    updater = Updater(os.environ['TG_BOT_TOKEN'])
    dispatcher: Dispatcher = updater.dispatcher

    with open('quiz.json', 'r', encoding='UTF-8') as file:
        dispatcher.bot_data['questions'] = list(json.load(file).items())

    dispatcher.bot_data['redis'] = redis.Redis(host=os.environ['REDIS_HOST'],
                                               port=os.environ['REDIS_PORT'], password=os.environ['REDIS_PASSWORD'])

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECT_ACTION:[
                MessageHandler(filters=Filters.text([NEW_QUESTION]), callback=new_question),
            ],
            ANSWER_QUESTION:[
                MessageHandler(filters=Filters.text([GIVE_UP]), callback=give_up),
                MessageHandler(filters=None, callback=process_user_answer),
                CallbackQueryHandler(cancel_input, pattern=CANCEL_INPUT)
            ],
            YES_OR_NO_REPEAT:[
                MessageHandler(filters=Filters.text([NO]), callback=start),
                MessageHandler(filters=Filters.text([YES]), callback=repeat_question)
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
