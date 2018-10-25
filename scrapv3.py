import asyncio
import json
import logging
from asyncio import Queue

import aiohttp

from processor.battles_processor import BattlesProcessor


async def fetch(session, url, headers):
    async with session.get(url, headers=headers) as response:
        return await response.json()


async def get_battles(user):
    headers = {
        'auth': "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NTI4LCJpZGVuIjoiNDQ4OTc2OTcyOTcwNzIxMjgwIiwibWQiOnt9fQ.92AuxAPbJ8pop8HnPNFVhyFLjm4GxfEQ_dNsnDgO4DM"
    }

    url = 'https://api.royaleapi.com/player/{}/battles'.format(user)

    async with aiohttp.ClientSession() as session:
        return await fetch(session, url, headers)

logging.basicConfig(level=logging.DEBUG)


async def scrap(task, queue, users, decks):
    global MAX_USERS

    while not queue.empty() and len(decks) < MAX_DECKS and MAX_USERS > 0:
        MAX_USERS -= 1
        print(task, "Total of decks", len(decks))
        #print(task, "Max users: ", MAX_USERS)

        user = queue.get_nowait()
        try:
            data = await get_battles(user)
        except Exception as e:
            queue.put_nowait(user)
            continue
        processed = processor.process(data)

        decks.extend(processed['decks'])
        users_found = set(processed['users']) - users
        users |= users_found

        for user in users_found:
            queue.put_nowait(user)


initial_users = ["82L08CJG0", "2GRJC90L8", "8C2LPGJGV", "JYR20QGU", "QYJ9U228", "Y9YRGV8R", "299JQ2LYR", "2CJLYYY0",
                 "LYPUC9YL", "2LVQGUGRJ", "82V2L9JLG", "2LJCJGUGY", "9QR9PLV8J", "8GJY8UQ8", "RPY0QJCP", "8J0YJ99JU",
                 "8GGL80PCC", "RJLJ00P2", "2PJPVRJ9C", "JC0LRYCU", "2UP0QLJG", "YCL0GJ82", "L90YGLC9", "2RRUPQC0U",
                 "P299QV0L", "8QJY9RP2Q", "8LYRLJYCR", "V9CPRG", "RCG99YVC", "C2J228YQ", "GP2RPCQ8", "2Q22UURYR",
                 "28GYV0LQL", "28JCUCRG", "8VYQPR9R", "890YQQCG", "YPU9U0Q9", "P0RRUGQ8V", "80JQPRGU8", "2GU2CJGL2",
                 "P0VVY2GY", "UYV920U"]

MAX_DECKS = 100000
MAX_USERS = 100000
MAX_TASKERS = 32  # len(initiall_users)

queue = Queue()
for initial_user in initial_users:
    queue.put_nowait(initial_user)

processor = BattlesProcessor()
users = set() | set(initial_users[:MAX_TASKERS])
decks = []

taskers = []
for i in range(MAX_TASKERS):
    taskers.append(scrap("Task "+str(i), queue, users, decks))

loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.wait(taskers))
loop.close()

with open('data/decks.json', 'w') as outfile:
    json.dump(decks, outfile)

with open('data/users.json', 'w') as outfile:
    json.dump(list(users), outfile)

with open('data/users_non_inspect.json', 'w') as outfile:
    new_queue = []
    while not queue.empty():
        new_queue.append(queue.get_nowait())
    json.dump(new_queue, outfile)
