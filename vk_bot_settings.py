from enum import Enum

from vk_api.keyboard import VkKeyboard, VkKeyboardColor


# data elements for per user caching
CURRENT_KEYBOARD = 1
CURRENT_QA = 2
CURRENT_STAGE = 3


class Commands():
    ASK_QUESTION = 'Новый вопрос'
    GIVE_UP = 'Сдаться'
    TRY_AGAIN_YES = 'Да'
    TRY_AGAIN_NO = 'Нет'
    ANY_TEXT = 0


class Stages(Enum):
    START_POINT = 0
    WAIT_FOR_ANSWER = 1
    TRY_AGAIN_YES_OR_NO = 2


# main keyboard
keyb_main: VkKeyboard = VkKeyboard(one_time=True)
keyb_main.add_button(Commands.ASK_QUESTION, color=VkKeyboardColor.PRIMARY)
keyb_main = keyb_main.get_keyboard()

# give up button
keyb_give_up: VkKeyboard = VkKeyboard(one_time=True)
keyb_give_up.add_button(Commands.GIVE_UP, color=VkKeyboardColor.NEGATIVE)
keyb_give_up = keyb_give_up.get_keyboard()

# Yes/No keyboard
keyb_yes_no: VkKeyboard = VkKeyboard(one_time=True)
keyb_yes_no.add_button(Commands.TRY_AGAIN_YES, color=VkKeyboardColor.POSITIVE)
keyb_yes_no.add_button(Commands.TRY_AGAIN_NO, color=VkKeyboardColor.NEGATIVE)
keyb_yes_no = keyb_yes_no.get_keyboard()