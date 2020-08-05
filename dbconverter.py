import sqlite3
from sqlite3 import Error
import os
import json


conn = sqlite3.connect('hierarchy.db')
c = conn.cursor()
c.execute('SELECT id, warns, kicks, bans FROM members')
values = c.fetchall()
conn.close()
values = list(filter(lambda value: value[1] or value[2] or value[3], values))


conn = sqlite3.connect('./storage/databases/offenses.db')
c = conn.cursor()
for value in values:
    c.execute('INSERT INTO offenses (id, warns, kicks, bans) VALUES (?, ?, ?, ?)', (value[0], value[1], value[2], value[3]))
conn.commit()
conn.close()