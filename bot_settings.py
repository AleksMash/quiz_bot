import datetime as dt

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton


# some constants
CURRENT_BUTTON, CURRENT_STEP, LAST_STEP,\
INPUT_DATA, CANCEL_INPUT, CURRENT_STAGE, NEXT_STAGE = map(str, range(7))

# stages
SELECT_ACTION = 1        # waiting for user clicks any of replymarkup button
ANY_TEXT_INPUT = 2       # waiting for user text input

# reply buttons
NEW_QUESTION = 'Новый вопрос'
GIVE_UP = 'Сдаться'
RATE = 'Мой счет'
TEMP = 'тест-кнопка'


# callback button data base name (and some of them are stages also - see main())

# Cancel button for cancelling input
CANCEL_MARKUP = InlineKeyboardMarkup.from_button(InlineKeyboardButton('Отмена', callback_data=CANCEL_INPUT))

# replymarkups
COMMON_REPLY_BUTTONS = ReplyKeyboardMarkup(
    [[NEW_QUESTION, GIVE_UP],
     [RATE, TEMP]]
)

#input steps for reply buttons (including type converter)
INPUT_STEPS = {}

# help inforamtion (now used as a plug for not finished functions)
# help_info ={
#     SEE_QUESTIONS: 'Показываем вопросы к докладу пользователя',
# }
