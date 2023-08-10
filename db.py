import json
import random

import redis, environs

env=environs.Env()
env.read_env()

redis_db = redis.Redis(host=env.str('REDIS_HOST'),
                 port=env.decimal('REDIS_PORT'),
                 password=env.str('REDIS_PASSWORD'))


with open('dev_data/quiz.json', 'r', encoding='UTF-8') as file:
    questions: list = json.load(file).values()

def save_user_question(user_id, question:str):
    redis_db.set(user_id, question)

def fetch_user_question(user_id):
    return redis_db.get(user_id)

def fetch_random_question() -> dict:
    return random.choice(questions)