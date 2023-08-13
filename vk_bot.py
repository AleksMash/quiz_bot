import random

import environs
import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from fuzzywuzzy import fuzz

import db
from vk_bot_settings import keyb_main, keyb_yes_no, keyb_give_up, Commands,\
    Stages, CURRENT_STAGE, CURRENT_QA, CURRENT_KEYBOARD


# cache for storing per user data
cache = {}

env=environs.Env()
env.read_env()


def get_user_cache(user_id):
    user_cache = cache.get(user_id)
    if not user_cache:
        user_cache = {
            CURRENT_KEYBOARD: None,
            CURRENT_QA: None,
            CURRENT_STAGE: None
        }
        cache[user_id] = user_cache
    return user_cache


def start(event, vk_api, text=None):
    vk_api.messages.send(
        user_id=event.user_id,
        message=text if text else 'Выбери действие',
        random_id=random.randint(1, 1000),
        keyboard=keyb_main
    )
    cache[event.user_id][CURRENT_KEYBOARD] = keyb_main
    return Stages.START_POINT


def ask_question(event, vk_api):
    current_stage = cache[event.user_id][CURRENT_STAGE]
    if current_stage == Stages.TRY_AGAIN_YES_OR_NO:
        question = cache[event.user_id][CURRENT_QA]
        msg_text = 'Повторяю вопрос\n\n:' + question['q']
    else:
        question = db.fetch_random_question()
        cache[event.user_id][CURRENT_QA] = question
        msg_text = question['q']
    vk_api.messages.send(
        user_id=event.user_id,
        message=msg_text,
        random_id=random.randint(1, 1000),
        keyboard=keyb_give_up
    )
    cache[event.user_id][CURRENT_KEYBOARD] = keyb_give_up
    return Stages.WAIT_FOR_ANSWER


def process_answer(event, vk_api):
    question = cache[event.user_id][CURRENT_QA]
    if fuzz.WRatio(question['a'], event.text) >= 70:
        return start(event, vk_api, 'Все верно! Для нового вопроса нажми кнопку "Новый вопрос"')
    vk_api.messages.send(
        user_id=event.user_id,
        message='Ответ неверный! Хотите попробовать ответить еще раз?',
        random_id=random.randint(1, 1000),
        keyboard=keyb_yes_no
    )
    cache[event.user_id][CURRENT_KEYBOARD] = keyb_yes_no
    return Stages.TRY_AGAIN_YES_OR_NO


def give_up(event, vk_api):
    send_message(event, vk_api, 'Правильный ответ:\n' + cache[event.user_id][CURRENT_QA]['a'])
    return start(event, vk_api)


def send_message(event, vk_api, text):
    current_keyboard = cache[event.user_id][CURRENT_KEYBOARD]
    vk_api.messages.send(
        user_id=event.user_id,
        message=text,
        random_id=random.randint(1, 1000),
        keyboard=current_keyboard
    )


def main():
    vk_session = vk.VkApi(token=env.str("VK_GROUP_TOKEN"))
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

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
            user_cache: dict = get_user_cache(event.user_id)
            if not user_cache[CURRENT_STAGE]:
                user_cache[CURRENT_STAGE] = start(event, vk_api, 'Выбери действие:')
                continue
            stage_callbacks = callbacks.get(user_cache[CURRENT_STAGE])
            if not stage_callbacks:
                user_cache[CURRENT_STAGE] = start(event, vk_api, "Упс! Нет обработчиков для текущего шага."
                                                           " Передай это сообщение разработчику. А пока попробуем"
                                                           " начать все сначала\n"
                                                           "Выбери действие:")
                continue
            func = stage_callbacks.get(event.text)
            if not func:
                func = stage_callbacks.get(Commands.ANY_TEXT)
                if not func:
                    send_message(event, vk_api, 'Команда не распознана или не активна на текущем шаге.'
                                                ' Выбери другую кнопку')
                    continue
            user_cache[CURRENT_STAGE] = func(event, vk_api)


if __name__ == "__main__":
    main()