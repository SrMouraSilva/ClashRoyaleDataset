import logging
import json
import requests
from collections import deque

from processor.battles_processor import BattlesProcessor


def get_battles(user):
    url = 'https://api.royaleapi.com/player/{}/battles'.format(user)

    headers = {
        'auth': "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NTI4LCJpZGVuIjoiNDQ4OTc2OTcyOTcwNzIxMjgwIiwibWQiOnt9fQ.92AuxAPbJ8pop8HnPNFVhyFLjm4GxfEQ_dNsnDgO4DM"
    }

    return requests.get(url, headers=headers).json()


logging.basicConfig(level=logging.DEBUG)

processor = BattlesProcessor()
users = set()
next_users = deque(["9J2PVVU8"])
decks = []

count = 10


def scrap(user):
    global count, users
    count -= 1
    if count < 0:
        users.clear()

    try:
        data = get_battles(user)
    except:
        next_users.append(user)
        return

    processed = processor.process(data)

    decks.extend(processed['decks'])
    users_found = set(processed['users']) - users
    users |= users_found
    next_users.extend(users_found)


import multiprocessing
cpus = 32

pool = multiprocessing.Pool(processes=cpus)
result = pool.map(scrap, next_users)

with open('decks.json', 'w') as outfile:
    json.dump(decks, outfile)

with open('users.json', 'w') as outfile:
    json.dump(list(users), outfile)
