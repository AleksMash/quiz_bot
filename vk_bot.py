import random, json, os

from dotenv import load_dotenv
import redis
import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from fuzzywuzzy import fuzz


# data ids  for per user caching in redis db
CURRENT_KEYBOARD = 1
QUESTION = 2
RIGHT_ANSWER = 3
CURRENT_STAGE = 4


class Commands():
    ASK_QUESTION = 'Новый вопрос'
    GIVE_UP = 'Сдаться'
    TRY_AGAIN_YES = 'Да'
    TRY_AGAIN_NO = 'Нет'
    ANY_TEXT = 0

class Stages():
    START_POINT = 1
    WAIT_FOR_ANSWER = 2
    TRY_AGAIN_YES_OR_NO = 3

# keyboards ids
KEYBOARD_MAIN = 1
KEYBOARD_GIVE_UP = 2
KEYBOARD_YES_NO = 3

keyboard_main: VkKeyboard = VkKeyboard(one_time=True)
keyboard_main.add_button(Commands.ASK_QUESTION, color=VkKeyboardColor.PRIMARY)

keyboard_give_up: VkKeyboard = VkKeyboard(one_time=True)
keyboard_give_up.add_button(Commands.GIVE_UP, color=VkKeyboardColor.NEGATIVE)

keyboard_yes_no: VkKeyboard = VkKeyboard(one_time=True)
keyboard_yes_no.add_button(Commands.TRY_AGAIN_YES, color=VkKeyboardColor.POSITIVE)
keyboard_yes_no.add_button(Commands.TRY_AGAIN_NO, color=VkKeyboardColor.NEGATIVE)

KEYBOARDS = {
    KEYBOARD_MAIN: keyboard_main.get_keyboard(),
    KEYBOARD_GIVE_UP: keyboard_give_up.get_keyboard(),
    KEYBOARD_YES_NO: keyboard_yes_no.get_keyboard()
}


def start(event, vk_api, redis_db, text=None, questions=None):
    vk_api.messages.send(
        user_id=event.user_id,
        message=text if text else 'Выбери действие',
        random_id=random.randint(1, 1000),
        keyboard=KEYBOARDS[KEYBOARD_MAIN]
    )
    redis_db.set(f'{event.user_id}_{CURRENT_KEYBOARD}', KEYBOARD_MAIN)
    return Stages.START_POINT


def ask_question(event, vk_api, questions, redis_db):
    current_stage = int(redis_db.get(f'{event.user_id}_{CURRENT_STAGE}').decode('UTF-8'))
    if current_stage == Stages.TRY_AGAIN_YES_OR_NO:
        question = redis_db.get(f'{event.user_id}_{QUESTION}').decode('UTF-8')
        msg_text = f'Повторяю вопрос\n\n:{question}'
    else:
        question = random.choice(questions)
        redis_db.set(f'{event.user_id}_{QUESTION}', question[0])
        redis_db.set(f'{event.user_id}_{RIGHT_ANSWER}', question[1])
        msg_text = question[0]
    vk_api.messages.send(
        user_id=event.user_id,
        message=msg_text,
        random_id=random.randint(1, 1000),
        keyboard=KEYBOARDS[KEYBOARD_GIVE_UP]
    )
    redis_db.set(f'{event.user_id}_{CURRENT_KEYBOARD}',KEYBOARD_GIVE_UP)
    return Stages.WAIT_FOR_ANSWER


def process_answer(event, vk_api, questions, redis_db):
    question = redis_db.get(f'{event.user_id}_{QUESTION}').decode('UTF-8')
    if fuzz.WRatio(question, event.text) >= 70:
        return start(event, vk_api, text='Все верно! Для нового вопроса нажми кнопку "Новый вопрос"',
                     redis_db=redis_db)
    vk_api.messages.send(
        user_id=event.user_id,
        message='Ответ неверный! Хотите попробовать ответить еще раз?',
        random_id=random.randint(1, 1000),
        keyboard=KEYBOARDS[KEYBOARD_YES_NO]
    )
    redis_db.set(f'{event.user_id}_{CURRENT_KEYBOARD}', KEYBOARD_YES_NO)
    return Stages.TRY_AGAIN_YES_OR_NO


def give_up(event, vk_api, questions, redis_db):
    right_answer = redis_db.get(f'{event.user_id}_{RIGHT_ANSWER}').decode('UTF-8')
    send_message(event, vk_api, f'Правильный ответ:\n\n{right_answer}', redis_db)
    return start(event, vk_api, redis_db=redis_db)


def send_message(event, vk_api, text, redis_db):
    current_keyboard = int(redis_db.get(f'{event.user_id}_{CURRENT_KEYBOARD}').decode('UTF-8'))
    vk_api.messages.send(
        user_id=event.user_id,
        message=text,
        random_id=random.randint(1, 1000),
        keyboard=KEYBOARDS[current_keyboard]
    )


def main():
    load_dotenv()
    vk_session = vk.VkApi(token=os.environ["VK_GROUP_TOKEN"])
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    with open('quiz.json', 'r', encoding='UTF-8') as file:
        questions: list = list(json.load(file).items())

    redis_db =  redis.Redis(host=os.environ['REDIS_HOST'], port=os.environ['REDIS_PORT'], password=os.environ['REDIS_PASSWORD'])

    # callback functions mapping to conversation stages and commands
    callbacks = {
        Stages.START_POINT: {Commands.ASK_QUESTION: ask_question},
        Stages.WAIT_FOR_ANSWER :{
            Commands.GIVE_UP: give_up,
            Commands.ANY_TEXT: process_answer
        },
        Stages.TRY_AGAIN_YES_OR_NO:{
            Commands.TRY_AGAIN_YES: ask_question,
            Commands.TRY_AGAIN_NO: start
        }
    }

    # start message listening
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            current_stage = int(redis_db.get(f'{event.user_id}_{CURRENT_STAGE}').decode('UTF-8'))
            if not current_stage:
                current_stage = start(event, vk_api, text='Выбери действие:', redis_db=redis_db)
                redis_db.set(f'{event.user_id}_{CURRENT_STAGE}',current_stage)
                continue
            stage_callbacks = callbacks.get(current_stage)
            if not stage_callbacks:
                current_stage = start(event, vk_api, text="Упс! Нет обработчиков для текущего шага."
                                                           " Передай это сообщение разработчику. А пока попробуем"
                                                           " начать все сначала\n"
                                                           "Выбери действие:", redis_db=redis_db)
                redis_db.set(f'{event.user_id}_{CURRENT_STAGE}', current_stage)
                continue
            func = stage_callbacks.get(event.text)
            if not func:
                func = stage_callbacks.get(Commands.ANY_TEXT)
                if not func:
                    send_message(event, vk_api, 'Команда не распознана или не активна на текущем шаге.'
                                                ' Выбери другую кнопку', redis_db)
                    continue
            redis_db.set(f'{event.user_id}_{CURRENT_STAGE}', func(event, vk_api,
                                                                  questions=questions, redis_db=redis_db))


if __name__ == "__main__":
    main()