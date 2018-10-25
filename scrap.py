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

MAX_DECKS = 10
MAX_USERS = 100000
while next_users and MAX_USERS > 0:
    MAX_USERS -= 1
    user = next_users.pop()
    if len(decks) > MAX_DECKS:
        break

    print(len(decks))

    try:
        data = get_battles(user)
    except:
        next_users.append(user)
        continue
    processed = processor.process(data)

    decks.extend(processed['decks'])
    users_found = set(processed['users']) - users
    users |= users_found
    next_users.extend(users_found)


with open('decks.json', 'w') as outfile:
    json.dump(decks, outfile)

with open('users.json', 'w') as outfile:
    json.dump(list(users), outfile)
