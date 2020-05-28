import sqlite3
from sqlite3 import Error
import os
import json


database = f"{os.getcwd()}\\hierarchy.db"

conn = sqlite3.connect(database)
c = conn.cursor()
with open('hierarchy.json') as json_file:
    hierarchy = json.load(json_file)

for person in hierarchy:
    userid = int(person["user"])
    items = ""
    inuse = ""
    for item in person["items"]:
        items = f'{items} {item}'
    for item in person["inuse"]:
        inusename = item["name"]
        inusetimer = item["timer"]
        inuse = f'{inuse} {inusename} {inusetimer}'
    c.execute(f'INSERT INTO members (id, money, workc, jailtime, stealc, rpsc, bank, bankc, total, hbank, heistamount, items, inuse, storage, isworking, tokens) VALUES ({userid}, {person["money"]}, {person["workc"]}, {person["jailtime"]}, {person["stealc"]}, {person["rpsc"]}, {person["bank"]}, {person["bankc"]}, {person["total"]}, {person["hbank"]}, {person["heistamount"]}, ?, ?, {person["storage"]}, ?, {person["tokens"]});', (items, inuse, 'False'))







conn.commit()
conn.close()
