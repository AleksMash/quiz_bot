import datetime as dt

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup


# some constants
CURRENT_STATE, INPUT_STEP, LAST_STEP, INPUT_DATA, CANCEL_INPUT = range(5)

# stages
WAIT_FOR_BUTTONS, INPUT_USER_INFO = map(lambda x: 'stage_'+chr(x), range(2))

# callback button data base name (and some of them are stages also - see main())


# input steps for handling user input step by step with type checking
# input_steps = {
#     NEW_EVENT:{
#         'last_step':3,
#         0:('Введите тему митапа', str),
#         1:('Введите описание бота', str),
#         2:('Введите дату начала', dt.date.fromisoformat),
#         3:('Введите дату окончания', dt.date.fromisoformat)
#     }
# }

# keyboards with static callback data


# Cancel button for cancelling input
CANCEL_MARKUP = InlineKeyboardMarkup.from_button(InlineKeyboardButton('Отмена', callback_data=CANCEL_INPUT))


# replymarkups
COMMON_REPLY_BUTTONS = ReplyKeyboardMarkup(
    [['Новый вопрос', 'Сдаться'],
     ['Мой счет']]
)

# help inforamtion (now used as a plug for not finished functions)
# help_info ={
#     SEE_QUESTIONS: 'Показываем вопросы к докладу пользователя',
# }
