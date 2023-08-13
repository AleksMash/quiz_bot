import datetime as dt

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton


# some constants
CURRENT_BUTTON, CURRENT_STEP, LAST_STEP,\
INPUT_DATA, CANCEL_INPUT, CURRENT_STAGE, NEXT_STAGE,\
CURRENT_QUESTION = map(str, range(8))

# conversation stages
SELECT_ACTION = 1       # waiting for user clicks any of replymarkup button
ANSWER_QUESTION = 2     # waiting for user answer
YES_OR_NO_REPEAT = 3 # wait for user choice to

# reply buttons
NEW_QUESTION = 'Новый вопрос'
GIVE_UP = 'Сдаться'
RATE = 'Мой счет'
YES = 'Да'
NO = 'Нет'

# Cancel button for cancelling input
CANCEL_MARKUP = InlineKeyboardMarkup.from_button(InlineKeyboardButton('Отмена', callback_data=CANCEL_INPUT))

# replymarkups
KB_START = ReplyKeyboardMarkup(
    [[NEW_QUESTION, GIVE_UP]]
)

KB_YES_NO = ReplyKeyboardMarkup(
    [[YES, NO]]
)


# input steps mapping to stages (including type converter)
# использована заготовка из моего другого бота. В данном проекте у нас только одношаговый ввод
INPUT_STEPS = {
    ANSWER_QUESTION:[('Введите свой ответ', str)]
}
