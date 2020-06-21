import sqlite3
from sqlite3 import Error


conn = sqlite3.connect('hierarchy.db')
c = conn.cursor()
c.execute('SELECT id, total FROM members WHERE total > 0 ORDER BY total DESC')
hierarchy = c.fetchall()
c.execute('SELECT id, total FROM members')
temp = c.fetchall()
conn.close()
print(temp)
print('\n\n\n')
print(hierarchy)
userid = int(input("Enter id: "))
find = int(input("Enter range: "))
ids=[]
for x in hierarchy:
    ids.append(x[0])
try:
    index = ids.index(userid)
except ValueError:
    hierarchy.append((userid, 0))
    ids.append(userid)
    index = ids.index(userid)


lower_index = index-find

if lower_index < 0:
    lower_index = 0

higher_index = index+find+1
length = len(hierarchy)

if higher_index > length:
    higher_index = length

result = hierarchy[lower_index:higher_index]


print(result)